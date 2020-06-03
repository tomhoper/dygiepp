import sys
import os 
import json
from pathlib import Path
import pathlib
import argparse
"""
usage:
python dygie/data/merge_corpus.py --root ../coviddata/ --dataset_list scierc,chemprot
"""

def merge_datasets(rootdir, dataset_list):

  combodir = rootdir / "combos"
  rootdir = rootdir /"UnifiedData"

  for effect in [True,False]:
    train_data_list = []
    dev_data_list = []
    test_data_list = []
    for item in dataset_list:
      print(item, effect)
      if effect == False:
        train_path = rootdir.joinpath(item).joinpath('mapped/mech/train.json')
        dev_path = rootdir.joinpath(item).joinpath('mapped/mech/dev.json')
        test_path = rootdir.joinpath(item).joinpath('mapped/mech/test.json')

      else:
        train_path = rootdir.joinpath(item).joinpath('mapped/mech_effect/train.json')
        dev_path = rootdir.joinpath(item).joinpath('mapped/mech_effect/dev.json')
        test_path = rootdir.joinpath(item).joinpath('mapped/mech_effect/test.json')
      
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

    if effect:
      path = combodir.joinpath('_'.join(dataset_list)).joinpath("mapped").joinpath("mech_effect")
    else:
      path = combodir.joinpath('_'.join(dataset_list)).joinpath("mapped").joinpath("mech")

    pathlib.Path(path).mkdir(parents=True, exist_ok=True) 

    print("Directory '%s' created" %path)
    output_file_train = open(path.joinpath('train.json'), "w")
    output_file_dev = open(path.joinpath('dev.json'), "w")
    output_file_test = open(path.joinpath('test.json'), "w")

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


  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('--dataset_list',type=str, required=True)
  parser.add_argument('--root',
                        type=Path,
                        help='path to data dir root',
                        default='../coviddata',
                        required=True)

  args = parser.parse_args()
  rootdir = args.root

  merge_datasets(rootdir, args.dataset_list.split(','))


    # merging_list = sys.argv[1:]
    # if merging_list[-1] = "effect":
    #   merge_datasets(merging_list[:-1], effect=True)
    # else:
    #   merge_datasets(merging_list, effect=False)

