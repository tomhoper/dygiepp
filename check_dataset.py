import json

dataset_path = "/data/aida/covid_aaai/"
dataset_path_suffix = "/mapped/mech_effect/"
dataset_name = "UnifiedData/covid_anno_par_madeline_final"
gold_file = open(dataset_path + "gold_madeline_sentences_matchcd/mech_effect/gold_par.tsv")
input_train_file = open(dataset_path + dataset_name + dataset_path_suffix + 'train.json')
input_dev_file = open(dataset_path + dataset_name + dataset_path_suffix + 'dev.json')
input_test_file = open(dataset_path + dataset_name + dataset_path_suffix + 'test.json')

train_data = [json.loads(line) for line in input_train_file]
train_ids = []
dev_data = [json.loads(line) for line in input_dev_file]
dev_ids = []
test_data = [json.loads(line) for line in input_test_file]
test_ids = []

gold_list = []
gold_ids  = []
for line in gold_file:
  line_parts = line[:-1].split("\t")
  if line_parts[0].replace("+", "") not in gold_ids:
    gold_ids.append(line_parts[0].replace("+", ""))

for item in train_data:
  if item["doc_key"].replace("+", "") not in train_ids:
    train_ids.append(item["doc_key"].replace("+", ""))

for item in dev_data:
  if item["doc_key"].replace("+", "") not in dev_ids:
    dev_ids.append(item["doc_key"].replace("+", ""))

for item in test_data:
  if item["doc_key"].replace("+", "") not in test_ids:
    test_ids.append(item["doc_key"].replace("+", ""))
# import pdb; pdb.set_trace()

test_dev_intesection = [x for x in test_ids if x in dev_ids]
train_dev_intesection = [x for x in train_ids if x in dev_ids]
train_test_intesection = [x for x in train_ids if x in test_ids]
gold_test_intesection = [x for x in gold_ids if x not in test_ids]
print(test_dev_intesection)
print(train_dev_intesection)
print(train_test_intesection)
print(gold_test_intesection)
print(len(train_ids))
print(len(dev_ids))
print(len(test_ids))
print(len(gold_ids))
