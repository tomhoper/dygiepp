"""
Find the docs with NaN's in them.
"""

import json
import sys
import tqdm
import itertools
import os

import torch

from allennlp import data
from allennlp.data import fields
from allennlp import modules
from allennlp.nn import util


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def get_embedder(bert_version):
    tok_indexers = {"bert": data.token_indexers.PretrainedTransformerMismatchedIndexer(
        bert_version)}
    token_embedder = modules.token_embedders.PretrainedTransformerMismatchedEmbedder(
        bert_version)
    embedder = modules.text_field_embedders.BasicTextFieldEmbedder({"bert": token_embedder})
    embedder.to("cuda:0")

    return tok_indexers, embedder


def check_nan_grads(words, tok_indexers, embedder):
    "Encode a list of words, take a gradient, and check for NaN's."
    # Convert words to tensor dict.
    vocab = data.Vocabulary()
    text_field = fields.TextField(
        [data.Token(word) for word in words], tok_indexers)
    text_field.index(vocab)
    token_tensor = text_field.as_tensor(text_field.get_padding_lengths())
    tensor_dict = text_field.batch_tensors([token_tensor])
    tensor_dict = util.move_to_device(tensor_dict, 0)

    if torch.any(tensor_dict["bert"]["offsets"] == -1):
        return False
    else:
        return True


def check_doc(doc, tok_indexers, embedder):
    sents = doc["sentences"]
    for sent in sents:
        if not check_nan_grads(sent, tok_indexers, embedder):
            return False
    else:
        return True


####################

in_dir = "data/chemprot/mapped"
out_dir = "data/chemprot/nan-docs"

# Check all folds from both mech and mech-effect.
folds = ["train", "dev", "test"]
variants = ["mech", "mech_effect"]

# Make output dirs.
for variant in variants:
    os.makedirs(f"{out_dir}/{variant}", exist_ok=True)

# Use SciBERT.
tok_indexers, embedder = get_embedder("allenai/scibert_scivocab_uncased")

# Loop over all combinations and dump offending docs to file.
for fold, variant in itertools.product(folds, variants):
    in_file = f"{in_dir}/{variant}/{fold}.json"
    output_file = f"{out_dir}/{variant}/{fold}.txt"

    with open(output_file, "w") as f:
        dataset = load_jsonl(in_file)
        for doc in tqdm.tqdm(dataset):
            if not check_doc(doc, tok_indexers, embedder):
                print(doc["doc_key"], file=f)
