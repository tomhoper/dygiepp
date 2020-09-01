import os
import multiprocessing
import pandas as pd
import spacy
from glob import glob
import time
import json
from collections import Counter
import random
import argparse
import pathlib
from pathlib import Path
random.seed(100)


# OUT_DIR_PARTITIONS = "/data/aida/cord19_partitions/jsons/"
# OUT_DIR_SENTENCES = "/data/aida/cord19_sentences/jsons/"

OUT_DIR_PARTITIONS = "/data/aida/covid_annotation_data/jsons/"
OUT_DIR_SENTENCES = "/data/aida/covid_annotation_data/jsons/"
NLP = spacy.load("en_core_web_sm")


def process_paragraph_sentences(paragraph):
    res = []
    text = NLP(paragraph)
    for sent in text.sents:
        tokens = [x.text for x in sent]
        if len(tokens) < 500:
            res.append(tokens)
        else:
            while tokens:
                res.append(tokens[:500])
                tokens = tokens[500:]
    return res

def process_paragraph_partition(paragraph):
    res = []
    text = NLP(paragraph)
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        if len(tokens) < 500:
          if len(all_tokens) + len(tokens) > 500:
            res.append(all_tokens)
            all_tokens = tokens
          else:
            all_tokens = all_tokens + tokens
        else:
            res.append(all_tokens)
            while len(tokens) > 500:
                res.append(tokens[:500])
                tokens = tokens[500:]      
            all_tokens = tokens
    res.append(all_tokens)
    return res

def process_abstract_metadata_file_partition(abstract, paper_id):
    # import pdb; pdb.set_trace()
    sents = process_paragraph_partition(abstract)
    return dict(doc_key=f"{paper_id}_abstract",
                sentences=sents)

def process_abstract_metadata_file_sentence(abstract, paper_id):
    # import pdb; pdb.set_trace()
    sents = process_paragraph_sentences(abstract)
    return dict(doc_key=f"{paper_id}_abstract",
                sentences=sents)


def read_data_set_indexes(dataset_path, dataset_name="covid_anno_par_madeline_final"):
    id_list = []

    dataset_path_suffix = "/mapped/mech_effect/"
    dataset_name = "UnifiedData/covid_anno_par_madeline_final"

    input_train_file = open(dataset_path + dataset_name + dataset_path_suffix + 'train.json')
    input_dev_file = open(dataset_path + dataset_name + dataset_path_suffix + 'dev.json')
    input_test_file = open(dataset_path + dataset_name + dataset_path_suffix + 'test.json')

    train_data = [json.loads(line) for line in input_train_file]
    train_ids = []
    dev_data = [json.loads(line) for line in input_dev_file]
    dev_ids = []
    test_data = [json.loads(line) for line in input_test_file]
    test_ids = []

    for item in train_data:
      if item["doc_key"].replace("+", "") not in id_list:
        id_list.append(item["doc_key"].replace("+", ""))

    for item in dev_data:
      if item["doc_key"].replace("+", "") not in id_list:
        id_list.append(item["doc_key"].replace("+", ""))

    for item in test_data:
      if item["doc_key"].replace("+", "") not in id_list:
        id_list.append(item["doc_key"].replace("+", ""))

    return id_list 
########################################
def process_metadata_csv(file_name, dataset_ids):

    data_list = pd.read_csv("metadata.csv", header=0, delimiter=',')
    for index, row in data_list.iterrows():
        if row['cord_uid'] + "_abstract_abstract" not in  dataset_ids:
            continue
        abstract = row["abstract"]
        if abstract == "":
            continue
        paper_id = row['cord_uid']
        try:
            # processed_abstract_partitions = process_abstract_metadata_file_partition(abstract, paper_id)
            processed_abstract_sentences = process_abstract_metadata_file_sentence(abstract, paper_id)
        except Exception:
            print(f"{paper_id}: failed processing")
            continue

        # newname_partitions = paper_id + ".jsonl"
        # with open(f"{OUT_DIR_PARTITIONS}/{newname_partitions}", "w") as f:
        #     print(json.dumps(processed_abstract_partitions), file=f)

        newname_sentences = paper_id + ".jsonl"
        with open(f"{OUT_DIR_SENTENCES}/{newname_sentences}", "w") as f:
            print(json.dumps(processed_abstract_sentences), file=f)

        print(f"{paper_id}: success")


#########################################

if __name__ == "__main__":
    id_list = read_data_set_indexes("/data/aida/covid_aaai/")
    process_metadata_csv("metadata.csv", id_list)
   









