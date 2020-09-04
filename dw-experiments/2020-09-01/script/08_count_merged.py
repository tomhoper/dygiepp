"""
Count the number of clusters we have left after the merge.
"""


import json
import pandas as pd
import tabulate


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


res = {}

for name in ["scierc", "merged", "genia-scierc"]:
    n_clusters = 0
    n_spans = 0
    fname = f"results/predictions/{name}.jsonl"
    data = load_jsonl(fname)
    for doc in data:
        clusters = doc["predicted_clusters"]
        n_clusters += len(clusters)
        n_spans += sum([len(x) for x in clusters])

    res[name] = {"n_clusters": n_clusters,
                 "n_spans": n_spans}

res = pd.DataFrame(res)
print(tabulate.tabulate(res, headers="keys", showindex="always", tablefmt="github"))
