import sys
import os 
import json

DATA_ROOT = "../../data/UnifiedData/"
COMBO_ROOT = "../../data/combo/"

def merge_datasets(dataset_list, effect):
  train_data_list = []
  dev_data_list = []
  test_data_list = []

  for item in dataset_list:
    if effect == False:
      train_path = DATA_ROOT + item + '/mapped/mech/train.json'
      dev_path = DATA_ROOT + item + '/mapped/mech/dev.json'
      test_path = DATA_ROOT + item + '/mapped/mech/test.json'
    else:
      train_path = DATA_ROOT + item + '/mapped/mech_effect/train.json'
      dev_path = DATA_ROOT + item + '/mapped/mech_effect/dev.json'
      test_path = DATA_ROOT + item + '/mapped/mech_effect/test.json'
    
    #reading the data 
    train_docs = [json.loads(line) for line in open(train_path)]
    if item == "srl":
      dev_docs = []
      test_docs = []
    else:
      dev_docs = [json.loads(line) for line in open(dev_path)]
      test_docs = [json.loads(line) for line in open(test_path)]

    #adding to what we have 
    print("adding " + str(len(train_docs)) + " train docs, " +  str(len(dev_docs))+ " dev docs " + str(len(test_docs)) + " test docs form " + item)
    train_data_list = train_data_list + train_docs
    dev_data_list = dev_data_list + dev_docs
    test_data_list = test_data_list + test_docs
    
  #
  path = os.path.join(COMBO_ROOT, '_'.join(dataset_list))
  if not os.path.exists(path):
    os.mkdir(path) 
  print("Directory '%s' created" %path)
  output_file_train = open(path + 'train.json', "w")
  output_file_dev = open(path + 'dev.json', "w")
  output_file_test = open(path + 'test.json', "w")

  for item in train_data_list:
    json.dump(item, output_file_train)
    output_file_train.write('\n')


  for item in dev_data_list:
    json.dump(item, output_file_dev)
    output_file_dev.write('\n')


  for item in test_data_list:
    json.dump(item, output_file_test)
    output_file_test.write('\n')


if __name__ == '__main__':

  merge_datasets(["scierc", "covid_anno"],  effect=True)
  merge_datasets(["scierc", "covid_anno"],  effect=False)

  merge_datasets(["scierc", "covid_anno_augment"],  effect=True)
  merge_datasets(["scierc", "covid_anno_augment"],  effect=False)

  merge_datasets(["scierc", "srl"],  effect=True)
  merge_datasets(["scierc", "srl"],  effect=False)

  merge_datasets(["scierc", "chemprot"],  effect=True)
  merge_datasets(["scierc", "chemprot"],  effect=False)

  merge_datasets(["scierc", "srl", "covid_anno"],  effect=True)
  merge_datasets(["scierc", "srl", "covid_anno"],  effect=False)

  merge_datasets(["scierc", "srl", "covid_anno_augment"],  effect=True)
  merge_datasets(["scierc", "srl", "covid_anno_augment"],  effect=False)


  merge_datasets(["scierc", "chemprot", "covid_anno"],  effect=True)
  merge_datasets(["scierc", "chemprot", "covid_anno"],  effect=False)

  merge_datasets(["scierc", "chemprot", "covid_anno_augment"],  effect=True)
  merge_datasets(["scierc", "chemprot", "covid_anno_augment"],  effect=False)


  merge_datasets(["scierc", "chemprot", "srl", "covid_anno"],  effect=True)
  merge_datasets(["scierc", "chemprot", "srl", "covid_anno"],  effect=False)

  merge_datasets(["scierc", "chemprot", "srl", "covid_anno_augment"],  effect=True)
  merge_datasets(["scierc", "chemprot", "srl", "covid_anno_augment"],  effect=False)


    # merging_list = sys.argv[1:]
    # if merging_list[-1] = "effect":
    #   merge_datasets(merging_list[:-1], effect=True)
    # else:
    #   merge_datasets(merging_list, effect=False)

