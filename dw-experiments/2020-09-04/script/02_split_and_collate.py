"""
Create train / dev / test splits, and collate.
"""


import json
import random
import os
import subprocess


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


# data = load_jsonl("data/processed/events.jsonl")
# random.seed(76)
# random.shuffle(data)


# # Split the data
# # 200 test, 150 dev, train for the rest.
# res = {"train": data[350:],
#        "dev": data[200:350],
#        "test": data[:200]}

# out_dir = "data/processed/split"
# os.makedirs(out_dir, exist_ok=True)
# for name, fold in res.items():
#     save_jsonl(fold, f"{out_dir}/{name}.jsonl")


# Collate the data
collate_path = "scripts/data/shared/collate.py"

cmd = ["python", collate_path,
       "data/processed/split",
       "data/processed/collated"]
subprocess.run(cmd)
