"""
The results are so good I want to make sure the folds don't overlap.
"""

import json
import itertools


def list_to_tuple(xs):
    "Convert a nested list into a nested tuple."
    if isinstance(xs, list):
        return tuple([list_to_tuple(x) for x in xs])
    else:
        return xs


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


names = ["train", "dev", "test"]

folds = {}
for name in names:
    folds[name] = load_jsonl(f"data/processed/collated/{name}.jsonl")

sentences = {}
for name in names:
    sentences[name] = [list_to_tuple(entry["sentences"]) for entry in folds[name]]

# Make sure all sentences are unique.
for name, sents in sentences.items():
    assert len(sents) == len(set(sents))

# Make sure there are no shared sentences between folds.
for fold1, fold2 in itertools.combinations(names, 2):
    shared = set(sentences[fold1]) & set(sentences[fold2])
    assert len(shared) == 0
