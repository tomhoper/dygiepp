"""
Merge results into a sinlge .csv.
"""

import itertools
import json
from pathlib import Path
import pandas as pd

metric_dir = "results/metrics"

fnames = Path(metric_dir).rglob("*dev.json")


def process_one(fname):
    data = json.load(open(fname))
    prod = itertools.product(["ner", "relation"],
                             ["precision", "recall", "f1"])
    keys = [f"_covid__{task}_{metric}" for task, metric in prod]
    kept = {k.replace("_covid__", ""): data[k] for k in keys}
    name = fname.parts[-1].split("-dev")[0]
    kept["name"] = name
    return kept



results = [process_one(fname) for fname in fnames]
results = pd.DataFrame(results).set_index("name")
results.to_csv("results/dev-metrics.tsv", sep="\t")
