"""
Shard the data into 4 files, for predictions on the 4 GPU's I have.
"""

import os
import json


in_dir = "data/partitions_small"
out_dir = "data/shards"

os.makedirs(out_dir, exist_ok=True)


def flatten(xxs):
    return [x for xs in xxs for x in xs]


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


in_files = [f"{in_dir}/{fname}" for fname in os.listdir(in_dir)]
in_data = [load_jsonl(fname) for fname in in_files]

in_data = flatten(in_data)

for entry in in_data:
    entry["dataset"] = "scierc"

first_quarter = int(len(in_data) / 4)
second_quarter = int(len(in_data) / 2)
third_quarter = int((3 / 4) * len(in_data))

groups = {1: in_data[:first_quarter],
          2: in_data[first_quarter:second_quarter],
          3: in_data[second_quarter:third_quarter],
          4: in_data[third_quarter:]}


for name, group in groups.items():
    out_file = f"{out_dir}/shard-{name}.jsonl"
    save_jsonl(group, out_file)
