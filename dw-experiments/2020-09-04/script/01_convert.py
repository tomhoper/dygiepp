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

def check_bounds(arg0, arg1, last_seen_index, dot_index):
    arg0_start, arg0_end = list(arg0)
    arg1_start, arg1_end = list(arg1)
    if not(arg0_start >= last_seen_index and arg0_start<=dot_index):
        return False
    if not(arg0_end >= last_seen_index and arg0_end<=dot_index):
        return False
    if not(arg1_start >= last_seen_index and arg1_start<=dot_index):
        return False
    if not(arg1_end >= last_seen_index and arg1_end<=dot_index):
        return False
    return True


def process_entry(entry):
    "Process a single sentence."
    doc_key = entry["meta"]["doc_key"]
    tokens = [tok["text"] for tok in entry["tokens"]]
    last_seen_index = 0
    json_dict = []
    while '.' in tokens[last_seen_index:]:
        dot_index = tokens[last_seen_index:].index('.') + last_seen_index
        part_tokes = tokens[last_seen_index:dot_index+1]

    # Get events as dict where keys are triggers, and values are lists of all
    # arg0's and arg1's.
        event_dict = get_event_dict(entry)

        # For each event in the event dict, create an event by taking outer product
        # of all arg0's and arg1's.
        events = []
        for trigger_tok, args in event_dict.items():
            if not(trigger_tok >= last_seen_index and trigger_tok <=dot_index):  #trigger not in this sentence
                continue
            prod = itertools.product(args["TRIGGER_ARG0"], args["TRIGGER_ARG1"])

            for arg0, arg1 in prod:
                if check_bounds(arg0, arg1, last_seen_index, dot_index):
                    new_arg0 = list(arg0)
                    new_arg1 = list(arg1)
                    new_arg0 = [x-last_seen_index for x in new_arg0]
                    new_arg1 = [x-last_seen_index for x in new_arg1]
                    new_trigger_tok = trigger_tok- last_seen_index
                    # if last_seen_index> 0:
                    #     import pdb; pdb.set_trace()
                    to_append = [[new_trigger_tok, "TRIGGER"],
                                 list(new_arg0) + ["ARG0"],
                                 list(new_arg1) + ["ARG1"]]
                    # import pdb; pdb.set_trace()
                    events.append(to_append)
        if events != []:
        # Create DyGIE-style json dict.
            json_dict.append({"doc_key": doc_key,
                     "dataset": "covid-event",
                     "sentences": [part_tokes],
                     "events": [events]})
        last_seen_index = dot_index + 1
        # if last_seen_index == 4:
        #     import pdb; pdb.set_trace()
        if last_seen_index >  len(tokens) or not ('.' in tokens[last_seen_index:]):
            if '.' not in '.' in tokens[last_seen_index:]:
                print(tokens[last_seen_index:])
            break
    return json_dict


####################

data = load_jsonl("data/raw/tom_event.jsonl")
MISSED = Counter()
processed = []
for entry in data:
    processed = processed + process_entry(entry)
# processed = [process_entry(entry) for entry in data]
save_jsonl(processed, "data/processed/events.jsonl")
