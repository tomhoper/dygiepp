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
            import pdb; pdb.set_trace()
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
    sents = process_paragraph(abstract)
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
                arg_seen = False
                ind_seen = -1
        if arg_seen == True:
            break
    count += 1
  return ind_seen

def reorder_format(anno_list):
    text_res = process_abstract_metadata_file(anno_list[0][1], anno_list[0][0])
    text_res['relations'] = [[]]
    text_res['ner'] = [[]]
    for annotation in anno_list:
        arg0_parts = process_paragraph(annotation[2])[0]
        arg1_parts = process_paragraph(annotation[3])[0]
        # import pdb; pdb.set_trace()
        ind0 = find_index(text_res['sentences'][0], arg0_parts)
        ind1 = find_index(text_res['sentences'][0], arg1_parts)
        if ind0 == -1 or ind1 == -1:
            print("hereeee")
            continue
        text_res['ner'][0].append([ind0, ind0 + len(arg0_parts)-1, "ENTITY"])
        text_res['ner'][0].append([ind1, ind1 + len(arg1_parts)-1, "ENTITY"])
        if "used" in annotation[4].lower() or 'do' in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "MECHANISM"])
        elif "effect" in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts)-1, ind1, ind1 + len(arg1_parts)-1, "EFFECT"])
        else:
            print("bad")
    # import pdb; pdb.set_trace()
    return text_res

def reorder_format_mech_only(anno_list):
    text_res = process_abstract_metadata_file(anno_list[0][1], anno_list[0][0])
    text_res['relations'] = [[]]
    text_res['ner'] = [[]]
    for annotation in anno_list:
        arg0_parts = process_paragraph(annotation[2])[0]
        arg1_parts = process_paragraph(annotation[3])[0]

        ind0 = find_index(text_res['sentences'][0], arg0_parts)
        ind1 = find_index(text_res['sentences'][0], arg1_parts)
        if ind0 == -1 or ind1 == -1:
            print("hereeee")
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

def create_annotated_covid(mech_flag, root_path, annotated_path):
    noise=False
    random.seed(100)
    if mech_flag== True:
        DATA_PATH= root_path + "/UnifiedData/covid_anno_par_madeline/mapped/mech/"
    else:
        DATA_PATH= root_path + "/UnifiedData/covid_anno_par_madeline/mapped/mech_effect/"
    
    data_dir = pathlib.Path(DATA_PATH)
    data_dir.mkdir(parents=True, exist_ok=True)
    TRAIN_COUNT = 80
    seen_ids = []

    doc_key_ind = {}
    madeline_keys = []
    other_keys = []
    input_file = open(annotated_path)
    madeline_annotated = {}
    other_annotation = {}
    count = 0
    for line in input_file:
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        # import pdb; pdb.set_trace()
        
        if line_parts[-1] == "madeline":
            # print("madeline")
            count += 1
            if line_parts[0] not in madeline_keys:
                madeline_keys.append(line_parts[0])
            if key not in madeline_annotated:
                madeline_annotated[key] = []
                madeline_annotated[key].append(line_parts)
            else:
                madeline_annotated[key].append(line_parts)
            if key in other_annotation:
                del other_annotation[key]
        else:
            if line_parts[0] not in other_keys:
                other_keys.append(line_parts[0])
            if key not in madeline_annotated:
                if key not in other_annotation and line_parts[0]:
                    other_annotation[key] = []
                    other_annotation[key].append(line_parts)
                else:
                    other_annotation[key].append(line_parts)
    # reorder_format(line_parts)

    unique_to_madeline = [doc_key for doc_key in madeline_keys if doc_key not in other_keys]
    print(len(madeline_keys))
    random.shuffle(unique_to_madeline)
    random.shuffle(madeline_keys)
    random.shuffle(other_keys)
    other_madeline = [doc_key for doc_key in madeline_keys if doc_key not in unique_to_madeline[0:40]]


    output_file_test = open(DATA_PATH + "test.json", "w")
    output_file_train = open(DATA_PATH + "train.json", "w")
    output_file_dev = open(DATA_PATH + "dev.json", "w")
    print(unique_to_madeline[0:40])
    for key in madeline_annotated:
        if mech_flag == True:
            data = reorder_format_mech_only(madeline_annotated[key])
        else:
            data = reorder_format(madeline_annotated[key])
        while data["doc_key"] in seen_ids:
            data["doc_key"] = data["doc_key"] + '+'
        seen_ids.append(data["doc_key"])
        if key[0] in unique_to_madeline[0:40]: #test data
            del data['relations']
            del data['ner']
            json.dump(data, output_file_test)
            output_file_test.write("\n")
        else:
            if key[0] in other_madeline[0:TRAIN_COUNT]:
                json.dump(data, output_file_train)
                output_file_train.write('\n')
            else:
                json.dump(data, output_file_dev)
                output_file_dev.write('\n')
            
    # if noise == False

def create_annotated_covid_noise(mech_flag, root_path, annotated_path):
    noise=True
    random.seed(100)

    if mech_flag== True:
        DATA_PATH_NOISY= root_path + "/UnifiedData/covid_anno_augmented_par_madeline/mapped/mech/"
    else:
        DATA_PATH_NOISY= root_path + "/UnifiedData/covid_anno_augmented_par_madeline/mapped/mech_effect/"
    
    data_dir = pathlib.Path(DATA_PATH_NOISY)
    data_dir.mkdir(parents=True, exist_ok=True)

    TRAIN_COUNT = 0
    seen_ids = []
    # TRAIN_COUNT_FROM_NOISE=80

    doc_key_ind = {}
    madeline_keys = []
    other_keys = []
    input_file = open(annotated_path)
    madeline_annotated = {}
    other_annotation = {}
    for line in input_file:
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        # import pdb; pdb.set_trace()
        if line_parts[-1] == "madeline":
            if line_parts[0] not in madeline_keys:
                madeline_keys.append(line_parts[0])
            if key not in madeline_annotated:
                madeline_annotated[key] = []
                madeline_annotated[key].append(line_parts)
            else:
                madeline_annotated[key].append(line_parts)
            if key in other_annotation:
                del other_annotation[key]
        else:
            if line_parts[0] not in other_keys:
                other_keys.append(line_parts[0])
            if key not in madeline_annotated:
                if key not in other_annotation and line_parts[0]:
                    other_annotation[key] = []
                    other_annotation[key].append(line_parts)
                else:
                    other_annotation[key].append(line_parts)

    # reorder_format(line_parts)

    unique_to_madeline = [doc_key for doc_key in madeline_keys if doc_key not in other_keys]
    print(len(madeline_keys))
    random.shuffle(unique_to_madeline)
    random.shuffle(madeline_keys)
    random.shuffle(other_keys)
    other_madeline = [doc_key for doc_key in madeline_keys if doc_key not in unique_to_madeline[0:40]]


    output_file_test_noise = open(DATA_PATH_NOISY + "test.json", "w")
    output_file_train_noise = open(DATA_PATH_NOISY + "train.json", "w")
    output_file_dev_noise = open(DATA_PATH_NOISY + "dev.json", "w")


    print(unique_to_madeline[0:40])
    for key in madeline_annotated:
        if mech_flag == True:
            data = reorder_format_mech_only(madeline_annotated[key])
        else:
            data = reorder_format(madeline_annotated[key])
        while data["doc_key"] in seen_ids:
            data["doc_key"] = data["doc_key"] + '+'
        seen_ids.append(data["doc_key"])
        if key[0] in unique_to_madeline[0:40]: #test data
            del data['relations']
            del data['ner']
            json.dump(data, output_file_test_noise)
            output_file_test_noise.write("\n")
        else:
            if key[0] in other_madeline[0:TRAIN_COUNT]:
                json.dump(data, output_file_train_noise)
                output_file_train_noise.write('\n')
                
            else:
                json.dump(data, output_file_dev_noise)
                output_file_dev_noise.write('\n')
     
    if noise:
        for key in other_annotation:
            if mech_flag == True:
                data = reorder_format_mech_only(other_annotation[key])
            else:
                data = reorder_format(other_annotation[key])

            while data["doc_key"] in seen_ids:
               data["doc_key"] = data["doc_key"] + '+'
            seen_ids.append(data["doc_key"])
            json.dump(data, output_file_train_noise)
            output_file_train_noise.write('\n')

def write_gold_file(mech_flag, root_path, annotated_path):
    random.seed(100)
    
    madeline_keys = []
    other_keys = []
    input_file = open(annotated_path)
    madeline_annotated = {}
    other_annotation = {}
    for line in input_file:
        # if "EFFECT" in line:
        #     import pdb; pdb.set_trace()
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        # import pdb; pdb.set_trace()
        if line_parts[-2] == "reject":
            print("reject") 
        if line_parts[-1] == "madeline":
            if line_parts[0] not in madeline_keys:
                madeline_keys.append(line_parts[0])
            if key not in madeline_annotated:
                madeline_annotated[key] = []
                madeline_annotated[key].append(line_parts)
            else:
                madeline_annotated[key].append(line_parts)
            if key in other_annotation:
                del other_annotation[key]
        else:
            if line_parts[0] not in other_keys:
                other_keys.append(line_parts[0])
            if key not in madeline_annotated:
                if key not in other_annotation and line_parts[0]:
                    other_annotation[key] = []
                    other_annotation[key].append(line_parts)
                else:
                    other_annotation[key].append(line_parts)

    # reorder_format(line_parts)

    unique_to_madeline = [doc_key for doc_key in madeline_keys if doc_key not in other_keys]
    print(len(madeline_keys))
    random.shuffle(unique_to_madeline)
    random.shuffle(madeline_keys)
    random.shuffle(other_keys)
    other_madeline = [doc_key for doc_key in madeline_keys if doc_key not in unique_to_madeline[0:40]]
    if mech_flag == True:
        output_file_path = root_path + "/gold_madeline/mech/"
    else:
        output_file_path = root_path + "/gold_madeline/mech_effect/"
        
    data_dir = pathlib.Path(output_file_path)
    data_dir.mkdir(parents=True, exist_ok=True)
    print(output_file_path)
    output_file = open(output_file_path + 'gold_par.tsv', "w")

    seen_ids = []
    print(unique_to_madeline[0:40])
    for key in madeline_annotated:
        if mech_flag==True:
            data = reorder_format(madeline_annotated[key])
        else:
            data = reorder_format_mech_only(madeline_annotated[key])
        while data["doc_key"] in seen_ids:
            data["doc_key"] = data["doc_key"] + '+'
        seen_ids.append(data["doc_key"])
        if key[0] in unique_to_madeline[0:40]: #test data
            for element in madeline_annotated[key]:
                # if "USED" in madeline_annotated[key]:
                if 'used' in element[4].lower() or 'do' in element[4].lower():
                    output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'MECHANISM\t' + element[5] + '\n')
                else:
                    if mech_flag == True:
                        output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'MECHANISM\t' + element[5] + '\n')
                    else:
                        output_file.write(data["doc_key"] + '\t' + key[1] + '\t' + element[2] + '\t' + element[3] + '\t' + 'EFFECT\t' + element[5] + '\n')

 


if __name__ == "__main__":

    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--annotation_path',
                        type=str,
                        default="bio_annotations/annotated_complete.tsv",
                        help='path to complete set of annotations',
                        required=False)
    parser.add_argument('--root',
                        type=str,
                        default="/data/aida/covid_clean/",
                        help='path to complete set of annotations',
                        required=False)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')
    parser.add_argument('--noise',
                        action='store_true')
    parser.add_argument('--gold',
                        action='store_true')

    args = parser.parse_args()

    if args.gold == True:
        write_gold_file(args.mech_effect_mode, args.root, args.annotation_path)
    else:
        if args.noise:
            create_annotated_covid_noise(args.mech_effect_mode, args.root, args.annotation_path)
        else:
            create_annotated_covid(args.mech_effect_mode, args.root, args.annotation_path)

