"""
Filter out the documents with NaN's or with no relations.
"""

import itertools
import json
import os


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


def cleanup(data, to_skip):
    res = []
    for doc in data:
        # Skip documents that create NaN's.
        if doc["doc_key"] in to_skip:
            continue
        # Skip documents with no relations.
        n_rels = [len(rels) for rels in doc["relations"]]
        if max(n_rels) == 0:
            continue

        # If we didn't hit a condition, append this to the dataset
        res.append(doc)

    return res


in_dir = "data/chemprot/mapped"
nan_dir = "data/chemprot/nan-docs"
out_dir = "data/chemprot/filtered"

# Check all folds from both mech and mech-effect.
folds = ["train", "dev", "test"]
variants = ["mech", "mech_effect"]

for variant in variants:
    os.makedirs(f"{out_dir}/{variant}", exist_ok=True)

for fold, variant in itertools.product(folds, variants):
    data = load_jsonl(f"{in_dir}/{variant}/{fold}.json")
    to_skip = [line.strip() for line in open(f"{nan_dir}/{variant}/{fold}.txt")]
    to_skip = [int(x) for x in to_skip]

    cleaned = cleanup(data, to_skip)
    out_file = f"{out_dir}/{variant}/{fold}.json"
    save_jsonl(cleaned, out_file)
