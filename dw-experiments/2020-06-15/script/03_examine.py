import json

from dygie.data.dataset_readers.data_structures import Dataset


data = [json.loads(line) for line in open("results/covid_anno_par_mech_effect_test.json")]

n_predicted = 0

for entry in data:
    assert len(entry["sentences"]) == len(entry["predicted_relations"]) == 1
    n_predicted += len(entry["predicted_relations"][0])


print(n_predicted)
