"""
Convert predictions to .tsv.
"""

from numpy import argmax
import json
import sys

sys.path.append('../shared')

from dygie.data.dataset_readers import document
from coref_to_tsv import to_tsv


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


for name in ["scierc", "genia-scierc", "merged"]:
    fname = f"results/predictions-collected/{name}.tsv"
    data = document.Dataset.from_jsonl(f"results/predictions-collected/{name}.jsonl")
    to_tsv(data, fname)
