import json
import os


data_dir = "data/jsons"
out_file = "data/merged.jsonl"

in_files = os.listdir(data_dir)

with open(out_file, "w") as f_out:
    for in_file in in_files:
        with open(f"{data_dir}/{in_file}") as f_in:
            for line in f_in:
                data = json.loads(line)
                data["dataset"] = "scierc"
                print(json.dumps(data), file=f_out)
