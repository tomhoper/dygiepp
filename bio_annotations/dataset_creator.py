"""
Preprocess data from LaTex parses. Need to run on S3 machine 3, that's where the
data are.
"""
ANNOTATION_PATH = "/bio_annotations/annotated_complete.tsv"

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

# counts = Counter()

# DATA_PATH = "2020-03-13"
OUT_DIR = "/data/aida/cord19/results_complete/input-json"
NLP = spacy.load("en_core_web_sm")

# os.makedirs(OUT_DIR, exist_ok=True)

# folders = os.listdir(DATA_PATH)


def tokenize(sent):
    # Sometimes the grobid parse crashes and gives outrageously long sentences.
    # If they're long, split. So this returns a list of lists, just in case the
    # sentences need to be split. If no splitting, it's just a list containing a
    # single list.
    processed = NLP(sent)
    tokens = [x.text for x in processed]

    # If it's not too long, return it.
    if len(tokens) < 500:
        return [tokens]

    # Otherwise split it by sentence and return.
    res = []
    for entry in processed.sents:
        tokens = [x.text for x in entry]
        # If it's less than 100 after splitting, append the sentence.
        if len(tokens) < 500:
            res.append(tokens)
        # Otherwise, just split it into chunks of 100.
        else:
            
            while tokens:
                res.append(tokens[:500])
                tokens = tokens[500:]

    return res


def process_paragraph(paragraph):
    res = []
    text = NLP(paragraph)
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        all_tokens = all_tokens + tokens
    return [all_tokens]



def process_abstract_metadata_file(abstract, paper_id):
    sents = process_paragraph(abstract.replace("  ", " "))
    return dict(doc_key=f"{paper_id}_abstract",
                section="Abstract",
                sentences=sents)



def find_index(sentence, arg_parts):
  ind_seen = -1
  count = 0
  arg_seen = False
  for i in range(len(sentence)):
    if sentence[i] == arg_parts[0]:
        arg_seen = True
        ind_seen = count
        for k in range(len(arg_parts)):
            if i + k < len(sentence) and arg_parts[k] != sentence[i + k]:
                if sentence[i + k].endswith('.') and arg_parts[k] != sentence[i + k][:len(sentence[i + k])-1]:
                    arg_seen = False
                    ind_seen = -1
        if arg_seen == True:
            break
    count += 1
  if ind_seen == -1:
    import pdb; pdb.set_trace()  
  return ind_seen

def scierc_format(anno_list):
    text_res = process_abstract_metadata_file(anno_list[0][1], anno_list[0][0])
    text_res['relations'] = [[]]
    text_res['ner'] = [[]]
    for annotation in anno_list:
        arg0_parts = process_paragraph(annotation[2].strip())[0]
        arg1_parts = process_paragraph(annotation[3].strip())[0]
        # 
        ind0 = find_index(text_res['sentences'][0], arg0_parts)
        ind1 = find_index(text_res['sentences'][0], arg1_parts)
        if ind0 == -1 or ind1 == -1:
            
            continue
        

        text_res['ner'][0].append([ind0, ind0 + len(arg0_parts)-1, "ENTITY"])
        text_res['ner'][0].append([ind1, ind1 + len(arg1_parts)-1, "ENTITY"])
        if "used" in annotation[4].lower() or 'do' in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "MECHANISM"])
        elif "effect" in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "EFFECT"])
        else:
            print("bad")
    # 
    return text_res

def scierc_format_mech_only(anno_list):
    text_res = process_abstract_metadata_file(anno_list[0][1], anno_list[0][0])
    text_res['relations'] = [[]]
    text_res['ner'] = [[]]
    for annotation in anno_list:
        arg0_parts = process_paragraph(annotation[2].strip())[0]
        arg1_parts = process_paragraph(annotation[3].strip())[0]

        ind0 = find_index(text_res['sentences'][0], arg0_parts)
        ind1 = find_index(text_res['sentences'][0], arg1_parts)
        if ind0 == -1 or ind1 == -1:
            continue
        text_res['ner'][0].append([ind0, ind0 + len(arg0_parts)-1, "ENTITY"])
        text_res['ner'][0].append([ind1, ind1 + len(arg1_parts)-1, "ENTITY"])
        if "used" in annotation[4].lower() or 'do' in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "MECHANISM"])
        elif "effect" in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "MECHANISM"])
        else:
            print("bad")
    return text_res


def write_scierc_format_data(annotation_dict, output_file, mech_only_flag, test_flag=False):
    seen_ids = []
    for key in annotation_dict:
        if mech_only_flag == True:
            data = scierc_format_mech_only(annotation_dict[key])
        else:
            data = scierc_format(annotation_dict[key])
        while data["doc_key"] in seen_ids:
            data["doc_key"] = data["doc_key"] + '+'
        seen_ids.append(data["doc_key"])
        if data['relations'] == [[]]:
            print("empty")
            continue
        #test data
        if test_flag == True:
            del data['relations']
            del data['ner']
        json.dump(data, output_file)
        output_file.write("\n")


def create_annotated_covid(mech_only_flag, root_path, annotated_path, test_keys, dev_keys, output_data_name):
    if mech_only_flag== True:
        DATA_PATH= root_path + "/UnifiedData/covid_anno_par_" + output_data_name + "/mapped/mech/"
    else:
        DATA_PATH= root_path + "/UnifiedData/covid_anno_par_" + output_data_name + "/mapped/mech_effect/"
    
    data_dir = pathlib.Path(DATA_PATH)
    data_dir.mkdir(parents=True, exist_ok=True)

    input_file = open(annotated_path)

    seen_ids = []
    
    test_annotation_dict = {}
    dev_annotation_dict = {}
    train_annotation_dict = {}

    for line in input_file:
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        # 
        if line_parts[-2] == "reject" or line_parts[-2] == "ignore":
            print("reject") 
            continue

        if line_parts[0] in test_keys:
            if key not in test_annotation_dict:
                test_annotation_dict[key] = []
                test_annotation_dict[key].append(line_parts)
            else:
                test_annotation_dict[key].append(line_parts)
        elif line_parts[0] in dev_keys:
            if key not in dev_annotation_dict:
                dev_annotation_dict[key] = []
                dev_annotation_dict[key].append(line_parts)
            else:
                dev_annotation_dict[key].append(line_parts)
        else:
            if key not in train_annotation_dict:
                train_annotation_dict[key] = []
                train_annotation_dict[key].append(line_parts)
            else:
                train_annotation_dict[key].append(line_parts)

    output_file_test = open(DATA_PATH + "test.json", "w")
    output_file_train = open(DATA_PATH + "train.json", "w")
    output_file_dev = open(DATA_PATH + "dev.json", "w")

    write_scierc_format_data(test_annotation_dict, output_file_test, mech_only_flag, test_flag=True)
    write_scierc_format_data(dev_annotation_dict, output_file_dev, mech_only_flag, test_flag=False)
    write_scierc_format_data(train_annotation_dict, output_file_train, mech_only_flag, test_flag=False)


def write_gold_file(mech_only_flag, root_path, annotated_path, test_keys, output_data_name):
    
    input_file = open(annotated_path)
    annotation_dict = {}
    if mech_only_flag == True:
        output_file_path = root_path + "/gold_" + output_data_name + "/mech/"
    else:
        output_file_path = root_path + "/gold_" + output_data_name + "/mech_effect/"

    data_dir = pathlib.Path(output_file_path)
    data_dir.mkdir(parents=True, exist_ok=True)
    print(output_file_path)
    output_file = open(output_file_path + 'gold_par.tsv', "w")
    
    for line in input_file:
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        if line_parts[-2] == "reject" or line_parts[-2] == "ignore":
            print("reject") 
            continue

        if line_parts[0] in test_keys:  #if the id matches the test ids we are looking for 
            if key not in annotation_dict:
                annotation_dict[key] = []
                annotation_dict[key].append(line_parts)
            else:
                annotation_dict[key].append(line_parts)

    seen_ids = []
    for key in annotation_dict:
        if mech_only_flag == True:
            data = scierc_format_mech_only(annotation_dict[key])
        else:
            data = scierc_format(annotation_dict[key])
        
        while data["doc_key"] in seen_ids:
            data["doc_key"] = data["doc_key"] + '+'
        
        seen_ids.append(data["doc_key"])
        for element in annotation_dict[key]:
                if 'used' in element[4].lower() or 'do' in element[4].lower():
                    output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'MECHANISM\t' + element[5] + '\n')
                else:
                    if mech_only_flag == True:
                        output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'MECHANISM\t' + element[5] + '\n')
                    else:
                        output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'EFFECT\t' + element[5] + '\n')

def get_test_indexes(annotated_path, testset_count=50, devset_count=30, random_seed=100):
    random.seed(random_seed)
    annotated_keys = []
    input_file = open(annotated_path)
    for line in input_file:
        line_parts = line[:-1].split("\t")
        
        if line_parts[0] not in annotated_keys:
            annotated_keys.append(line_parts[0])
    random.shuffle(annotated_keys)
    print(len(annotated_keys))
    return annotated_keys[:testset_count], annotated_keys[testset_count: testset_count + devset_count]

