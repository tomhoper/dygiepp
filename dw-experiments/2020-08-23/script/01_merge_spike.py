"""
Merge in the spike annotations with Aida's data. Use a variety of different weights.
"""


import json
import os
import subprocess
import torch
from tqdm import tqdm

from allennlp.data import token_indexers, fields, Vocabulary, Token

# Set this to point to the root of the DyGIE project.
DYGIE_PATH = "/data/dwadden/proj/dygie/dygiepp-new"


def flatten(xxs):
    return [x for xs in xxs for x in xs]


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


def filter_empty_strings(data):
    "Remove entries that have empty strings in them."
    cleaned_data = []

    for entry in data:
        # Throw out entries with empty strings.
        keep = True
        for sent in entry["sentences"]:
            keep &= all([tok != "" for tok in sent])

        if keep:
            cleaned_data.append(entry)

    discarded = len(data) - len(cleaned_data)
    total = len(data)
    if discarded:
        print(f"Discarded {discarded} / {total} Spike entries due to empty strings.")

    return cleaned_data


def filter_breaks_tokenizer(data):
    "Removes entries that break the tokenizer."
    tok_indexers = {"bert": token_indexers.PretrainedTransformerMismatchedIndexer(
        "allenai/scibert_scivocab_cased", max_length=512)}

    cleaned_data = []

    for entry in tqdm(data, total=len(data)):
        vocab = Vocabulary()
        keep = True
        # If there are any tokens that couldn't be indexed, skip this document.
        for sent in entry["sentences"]:
            text_field = fields.TextField(
                [Token(word) for word in sent], tok_indexers)
            text_field.index(vocab)
            token_tensor = text_field.as_tensor(text_field.get_padding_lengths())
            if torch.any(token_tensor["bert"]["offsets"] == -1).item():
                keep = False
        # If we didn't find any bad ones, then keep this entry.
        if keep:
            cleaned_data.append(entry)

    discarded = len(data) - len(cleaned_data)
    total = len(data)

    if discarded:
        print(f"Discarded {discarded} / {total} Spike entries due to un-indexable tokens.")

    return cleaned_data


def cleanup():
    """
    Do some initial cleanup.
    - Rename / throw out fields and split spike tokens.
    - Throw out the cases where sentences have empty tokens.
    - Throw out the cases where there's any token that messes up SciBERT.
    """
    in_dir = "data/raw"
    out_dir = "data/cleanup"

    # For COVID, rename the `section` field to be additional metadata.
    covid_in_dir = f"{in_dir}/covid"
    covid_out_dir = f"{out_dir}/covid"
    os.makedirs(covid_out_dir, exist_ok=True)
    for fold in ["train", "dev", "test"]:
        data = load_jsonl(f"{covid_in_dir}/{fold}.json")
        for entry in data:
            del entry["section"]

        save_jsonl(data, f"{covid_out_dir}/{fold}.json")

    # For Spike, thow out NER and split tokens.
    spike_in_dir = f"{in_dir}/spike"
    spike_out_dir = f"{out_dir}/spike"
    os.makedirs(spike_out_dir, exist_ok=True)
    for fold in ["train"]:
        data = load_jsonl(f"{spike_in_dir}/{fold}.jsonl")
        # Fix the sentences. Right now, it's a list of length-1 list of
        # space-separate tokens. Need to split the tokens out.
        for entry in data:
            # Flatten NER annotations and remove duplicates. Right now, there's
            # NER pairs for all relations.
            if len(entry["ner"]) != 1:
                flat = flatten(entry["ner"])
                to_dedup = [tuple(x) for x in flat]
                deduped = sorted(set(to_dedup))
                # The second set of brackets are correct.
                entry["ner"] = [[list(x) for x in deduped]]

            assert len(entry["ner"]) == 1

            new_sents = []
            sentences = entry["sentences"]

            for sent in sentences:
                if isinstance(sent, list):
                    split = sent[0].split(" ")
                elif isinstance(sent, str):
                    split = sent.split(" ")
                else:
                    raise Exception("Not expecting this.")
                new_sents.append(split)

            # There should be a single sentence per entry.
            assert len(new_sents) == 1
            entry["sentences"] = new_sents

        # Filter out data that has sentences with empty strings.
        cleaned_data = filter_breaks_tokenizer(filter_empty_strings(data))

        save_jsonl(cleaned_data, f"{spike_out_dir}/{fold}.jsonl")


def collate():
    """
    Collate the covid data and the spike data.
    """
    os.makedirs("data/collated/covid", exist_ok=True)
    # Collate COVID data.
    cmd = ["python", f"{DYGIE_PATH}/scripts/data/shared/collate.py",
           "data/cleanup/covid",
           "data/collated/covid",
           "--file_extension=json",
           "--dataset=covid"]
    subprocess.run(cmd)

    # Collate
    os.makedirs("data/collated/spike", exist_ok=True)
    cmd = ["python", f"{DYGIE_PATH}/scripts/data/shared/collate.py",
           "data/cleanup/spike",
           "data/collated/spike",
           "--dev_name=skip",
           "--test_name=skip",
           "--dataset=covid"]  # We want the spike data to the covid label namespace.
    subprocess.run(cmd)


def make_weighted_train_data(spike_exponent):
    out_dir = f"data/processed"
    covid_in = "data/collated/covid"
    spike_in = "data/collated/spike"

    # Merge the training data.
    train_covid = load_jsonl(f"{covid_in}/train.json")
    for entry in train_covid:
        entry["weight"] = 1.0

    train_spike = load_jsonl(f"{spike_in}/train.jsonl")
    for entry in train_spike:
        entry["weight"] = pow(10, spike_exponent)

    train = train_covid + train_spike
    save_jsonl(train, f"{out_dir}/train-spike-{-spike_exponent}.json")


def make_processed_data():
    out_dir = f"data/processed"
    os.makedirs(out_dir, exist_ok=True)

    for spike_exponent in [-4, -2, 0]:
        make_weighted_train_data(spike_exponent)

    covid_in = "data/collated/covid"
    for fold in ["train", "dev", "test"]:
        covid = load_jsonl(f"{covid_in}/{fold}.json")
        for entry in covid:
            entry["weight"] = 1.0
        save_jsonl(covid, f"{out_dir}/{fold}.json")


####################


def main():
    # Clean up the input data.
    cleanup()

    # Collate the spike and covid data.
    collate()

    # Make processed data, with the different Spike versions.
    make_processed_data()


if __name__ == "__main__":
    main()
