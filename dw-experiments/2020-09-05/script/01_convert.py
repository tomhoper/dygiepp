"""
Convert data to DyGIE format.
"""

import json
import itertools
from collections import Counter, defaultdict


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


def get_event_dict(entry):
    "Get dict mapping from triggers to their arg0's and arg1's."
    event_dict = defaultdict(lambda: {"TRIGGER_ARG0": [], "TRIGGER_ARG1": []})

    for relation in entry["relations"]:
        head = relation["head_span"]
        child = relation["child_span"]

        # Skip the ones that aren't trigger / arg relations.
        if head["label"] != "TRIGGER" or child["label"] != "ENTITY":
            MISSED["not_trigger_arg"] += 1
            continue

        # Skip if the trigger is more than one token.
        if head["token_start"] != head["token_end"]:
            MISSED["multi_token_trigger"] += 1
            continue

        trigger_tok = head["token_start"]
        arg_span = (child["token_start"], child["token_end"])
        arg_label = relation["label"]

        event_dict[trigger_tok][arg_label].append(arg_span)

    return event_dict


def process_entry(entry):
    "Process a single sentence."
    doc_key = entry["meta"]["doc_key"]
    tokens = [tok["text"] for tok in entry["tokens"]]

    # Get events as dict where keys are triggers, and values are lists of all
    # arg0's and arg1's.
    event_dict = get_event_dict(entry)

    # For each event in the event dict, create an event by taking outer product
    # of all arg0's and arg1's.
    events = []
    for trigger_tok, args in event_dict.items():
        prod = itertools.product(args["TRIGGER_ARG0"], args["TRIGGER_ARG1"])
        for arg0, arg1 in prod:
            to_append = [[trigger_tok, "TRIGGER"],
                         list(arg0) + ["ARG0"],
                         list(arg1) + ["ARG1"]]
            events.append(to_append)

    # Create DyGIE-style json dict.
    json_dict = {"doc_key": doc_key,
                 "dataset": "covid-event",
                 "sentences": [tokens],
                 "events": [events]}
    return json_dict


####################

data = load_jsonl("data/raw/tom_event.jsonl")
MISSED = Counter()

processed = [process_entry(entry) for entry in data]
save_jsonl(processed, "data/processed/events.jsonl")
