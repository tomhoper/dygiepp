import json
from collections import Counter

from dygie.data.dataset_readers.data_structures import Dataset


data = [json.loads(line) for line in open("results/covid_abstracts.json")]


n_predicted = 0


counts = Counter()

data = Dataset("results/covid_abstracts.json")
for entry in data:
    for sent in entry:
        if sent.predicted_relations:
            counts["ner"] += len(sent.predicted_ner)
            counts["relations"] += len(sent.predicted_relations)
            print(sent)
            for pred in sent.predicted_relations:
                print(f"- {pred}")
            print("\n" + 20 * "#" + "\n")

print(counts)
