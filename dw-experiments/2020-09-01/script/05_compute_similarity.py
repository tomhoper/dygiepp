import json
from typing import Tuple

import pandas as pd
from allennlp_models.coref.metrics.conll_coref_scores import Scorer


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def get_gold_clusters(gold_clusters):
    gold_clusters = [tuple(tuple(m) for m in gc) for gc in gold_clusters]
    mention_to_gold = {}
    for gold_cluster in gold_clusters:
        for mention in gold_cluster:
            mention_to_gold[mention] = gold_cluster
    return gold_clusters, mention_to_gold


def get_metric(scorers) -> Tuple[float, float, float]:
    metrics = (lambda e: e.get_precision(), lambda e: e.get_recall(), lambda e: e.get_f1())
    precision, recall, f1_score = tuple(
        sum(metric(e) for e in scorers) / len(scorers) for metric in metrics
    )

    return precision, recall, f1_score


def compare(clusts1, clusts2):
    "Given two sets of clusters from a collection of documents, compute F1."
    scorers = [Scorer(m) for m in (Scorer.muc, Scorer.b_cubed, Scorer.ceafe)]

    for clust1, clust2 in zip(clusts1, clusts2):
        clusters_one, mapping_one = get_gold_clusters(clust1)
        clusters_two, mapping_two = get_gold_clusters(clust2)

        for scorer in scorers:
            scorer.update(clusters_one, clusters_two, mapping_one, mapping_two)

    res = get_metric(scorers)
    res = {"p": res[0], "r": res[1], "f1": res[2]}
    return res


####################

res = {}


# Look at similarity of SciERC predictions.

one = load_jsonl("results/predictions-scierc/scierc.jsonl")
both = load_jsonl("results/predictions-scierc/genia-scierc.jsonl")

gold_one = [x["clusters"] for x in one]
gold_both = [x["clusters"] for x in both]
pred_one = [x["predicted_clusters"] for x in one]
pred_both = [x["predicted_clusters"] for x in both]

# Make sure gold annots have agreement of 1.
sim_gold = compare(gold_one, gold_both)
for k, v in sim_gold.items():
    assert v == 1

res["scierc_gold_scierc"] = compare(gold_one, pred_one)
res["scierc_gold_both"] = compare(gold_one, pred_both)
res["scierc_scierc_both"] = compare(pred_one, pred_both)


####################

# Look at similarity of covid predictions.

covid_one = load_jsonl("results/predictions/scierc.jsonl")
covid_both = load_jsonl("results/predictions/genia-scierc.jsonl")

covid_pred_one = [x["predicted_clusters"] for x in covid_one]
covid_pred_both = [x["predicted_clusters"] for x in covid_both]

res["covid_scierc_both"] = compare(covid_pred_one, covid_pred_both)

res = pd.DataFrame(res).T
res.to_csv("results/prediction-similarity.tsv", sep="\t", float_format="%0.4f")
