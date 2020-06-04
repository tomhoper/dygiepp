"""
Check consistency of the data for the COVID KG project.

Usage: python check_consistency.py [data-root].
"""

import sys
import os
import fnmatch
import json


def find(pattern, path):
    "Find files matching pattern."
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result



def check_one_file(fname):
    "Check that all fields in a file have consistent lengths."
    # Loop over all the lines. If we find a bug, return False. If we get to the
    # end, return True.
    keys_to_check = ["ner", "relations"]
    data = [json.loads(line) for line in open(fname)]
    for entry in data:
        n_sents = len(entry["sentences"])
        for key in keys_to_check:
            if key in entry:
                field = entry[key]
                field_length = len(field)
                if field_length != n_sents:
                    msg = f"File {fname}, doc_key {entry['doc_key']}: Expected {n_sents} entries in `{key}` but got {len(field)}."
                    print(msg)
                    return False

    return True


####################

data_root = sys.argv[1]
errors = []

all_files = find("*.json", data_root) + find("*.jsonl", data_root)
all_files = [x for x in all_files if "cached" not in x]
for filename in all_files:
    is_correct = check_one_file(filename)
    if not check_one_file(filename):
        errors.append(filename)
