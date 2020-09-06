"""
Convert predictions to `.tsv`.
"""

import pandas as pd
import os

from dygie.data.dataset_readers import document


def stringify(xs):
    return " ".join(xs)


def format_gold_events(sent):
    res = []
    for event in sent.events:
        arg0 = event.arguments[0]
        arg1 = event.arguments[1]
        entry = {"doc_key": sent.metadata["_orig_doc_key"],
                 "sentence": stringify(sent.text),
                 "arg0": stringify(arg0.span.text),
                 "trigger": event.trigger.token.text,
                 "arg1": stringify(arg1.span.text)}
        res.append(entry)
    return res


def format_predicted_events(sent):
    res = []
    for event in sent.predicted_events:
        arg0 = event.arguments[0]
        arg1 = event.arguments[1]
        entry = {"doc_key": sent.metadata["_orig_doc_key"],
                 "sentence": stringify(sent.text),
                 "arg0": stringify(arg0.span.text),
                 "trigger": event.trigger.token.text,
                 "arg1": stringify(arg1.span.text),
                 "arg0_logit": arg0.raw_score,
                 "trigger_logit": event.trigger.raw_score,
                 "arg1_logit": arg1.raw_score,
                 "arg0_softmax": arg0.softmax_score,
                 "trigger_softmax": event.trigger.softmax_score,
                 "arg1_softmax": arg1.softmax_score}
        res.append(entry)
    return res


def format_dataset(dataset):
    gold_events = []
    predicted_events = []

    for doc in dataset:
        for sent in doc:
            gold = format_gold_events(sent)
            predicted = format_predicted_events(sent)
            gold_events.extend(gold)
            predicted_events.extend(predicted)

    gold_events = pd.DataFrame(gold_events)
    predicted_events = pd.DataFrame(predicted_events)

    return gold_events, predicted_events


####################


in_dir = "results/predictions/covid-event-pubmedbert/decoded"
out_dir = "results/predictions/covid-event-pubmedbert/tsv"

os.makedirs(out_dir, exist_ok=True)

for fold in ["train", "dev", "test"]:
    dataset = document.Dataset.from_jsonl(f"{in_dir}/{fold}.jsonl")
    gold, pred = format_dataset(dataset)

    gold.to_csv(f"{out_dir}/{fold}-gold.tsv", sep="\t", float_format="%0.4f", index=False)
    pred.to_csv(f"{out_dir}/{fold}-predicted.tsv", sep="\t", float_format="%0.4f", index=False)
