"""
Compute F1 for exact match between gold and predicted events.
"""


from tabulate import tabulate
import pandas as pd

pred_dir = "results/predictions/covid-event-pubmedbert/tsv"


def compute_f1(counts):
    precision = counts["correct"] / counts["predicted"]
    recall = counts["correct"] / counts["gold"]
    f1 = (2 * precision * recall) / (precision + recall)
    return {"precision": precision,
            "recall": recall,
            "f1": f1}


def to_set(df):
    # Convert each row to a tuple and make a set out of the rows.
    res = []
    for _, row in df.iterrows():
        res.append(tuple(row.to_dict().values()))

    return set(res)


scores = {}

for fold in ["train", "dev", "test"]:
    gold = pd.read_table(f"{pred_dir}/{fold}-gold.tsv")
    pred = pd.read_table(f"{pred_dir}/{fold}-predicted.tsv")[gold.columns]

    gold_set = to_set(gold)
    pred_set = to_set(pred)

    counts = {"gold": len(gold_set),
              "predicted": len(pred_set),
              "correct": len(gold_set & pred_set)}

    scores[fold] = compute_f1(counts)

scores = pd.DataFrame(scores).T
scores.to_csv("results/summary-exact-match.tsv", sep="\t", float_format="%0.4f")

tabulated = tabulate(scores, tablefmt="github", showindex=True, headers="keys",
                     floatfmt="0.4f")
with open("results/summary-exact-match.md", "w") as f:
    f.write(tabulated)
