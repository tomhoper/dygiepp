"""
Collect results into table.
"""

import pandas as pd
import json
from tabulate import tabulate


in_dir = "results/metrics"

names = ["biomedroberta", "pubmedbert"]


def matches(name):
    fields = ["trig_class_precision", "trig_class_recall", "trig_class_f1",
              "arg_class_precision", "arg_class_recall", "arg_class_f1"]
    for field in fields:
        if field in name and "MEAN" in name:
            return True
    return False

res = {}
for name in names:
    metrics = json.load(open(f"{in_dir}/covid-event-{name}.json"))
    res[name] = {k: metrics[k] for k in metrics if matches(k)}

res = pd.DataFrame(res)
res.index = [x.split("__")[1] for x in res.index]

res.to_csv("results/summary.tsv", sep="\t", float_format="%0.4f")

tabulated = tabulate(res, tablefmt="github", showindex=True, headers="keys",
                     floatfmt="0.4f")
with open("results/summary.md", "w") as f:
    f.write(tabulated)
