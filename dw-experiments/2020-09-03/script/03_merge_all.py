"Collect shards and merge."


import json

from merge import merge_doc


def flatten(xxs):
    return [x for xs in xxs for x in xs]


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


FAILURE = "_FAILED_PREDICTION"

in_dir = "results/predictions"
out_file = "results/predictions-merged/predictions.jsonl"
failure_file = "results/predictions-merged/failed.txt"

scierc = [load_jsonl(f"{in_dir}/{shard}-scierc.jsonl")
          for shard in [1, 2, 3, 4]]
scierc = flatten(scierc)

genia_scierc = [load_jsonl(f"{in_dir}/{shard}-genia-scierc.jsonl")
                for shard in [1, 2, 3, 4]]
genia_scierc = flatten(genia_scierc)

keys_scierc = [x["doc_key"] for x in scierc]
keys_both = [x["doc_key"] for x in genia_scierc]
assert keys_scierc == keys_both
assert len(set(keys_scierc)) == len(keys_scierc)

res = []
with open(failure_file, "w") as f_failure:
    for doc_scierc, doc_both in zip(scierc, genia_scierc):
        assert doc_scierc["doc_key"] == doc_both["doc_key"]
        # Note the ones that failed and skip.
        if FAILURE in doc_scierc or FAILURE in doc_both:
            print(doc_scierc["doc_key"], file=f_failure)
            continue

        merged = merge_doc(doc_scierc, doc_both)
        res.append(merged)

save_jsonl(res, out_file)
