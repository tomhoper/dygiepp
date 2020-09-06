"""
Double check the performance metrics, just to make sure.
"""

import json
from collections import Counter


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def list_to_tuple(xs):
    if isinstance(xs, list):
        return tuple([list_to_tuple(x) for x in xs])
    else:
        return xs


def flatten(xxs):
    return [x for xs in xxs for x in xs]


def compute_f1(counts):
    precision = counts["correct"] / counts["predicted"]
    recall = counts["correct"] / counts["gold"]
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def dedup(xs):
    return tuple(sorted(set(xs)))


def convert_to_trig_and_args(events):
    triggers = list_to_tuple([x[0] for x in events])
    arguments = list_to_tuple(flatten([x[1:] for x in events]))
    return dedup(triggers), dedup(arguments)
    return triggers, arguments


dataset = load_jsonl("results/predictions/covid-event-pubmedbert/collated/test.jsonl")

counts = {"trigger": Counter(), "args": Counter()}

for doc in dataset:
    for gold, pred in zip(doc["events"], doc["predicted_events"]):
        gold_trigs, gold_args = convert_to_trig_and_args(gold)
        pred_trigs, pred_args = convert_to_trig_and_args(pred)

        counts["trigger"]["gold"] += len(gold_trigs)
        counts["trigger"]["predicted"] += len(pred_trigs)
        for pred_trig in pred_trigs:
            if pred_trig[:2] in gold_trigs:
                counts["trigger"]["correct"] += 1

        counts["args"]["gold"] += len(gold_args)
        counts["args"]["predicted"] += len(pred_args)
        for pred_arg in pred_args:
            if pred_arg[:3] in gold_args:
                counts["args"]["correct"] += 1


res = {"trigger": compute_f1(counts["trigger"]),
       "args": compute_f1(counts["args"])}

print(res)
