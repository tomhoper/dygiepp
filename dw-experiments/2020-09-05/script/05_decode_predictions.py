import json

from decode import decode


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)

####################


in_dir = "results/predictions/covid-event-pubmedbert/collated"
out_dir = "results/predictions/covid-event-pubmedbert/decoded"

for fold in ["train", "dev", "test"]:
    in_file = f"{in_dir}/{fold}.jsonl"
    out_file = f"{out_dir}/{fold}.jsonl"
    in_data = load_jsonl(in_file)
    out_data = decode(in_data)
    save_jsonl(out_data, out_file)
