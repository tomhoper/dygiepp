import json 
from pathlib import Path
import os
import json
import jsonlines
import glob
import sys
from pathlib import Path
from tqdm import tqdm
import argparse


def load_map_dict(map_path):
    with open(map_path,"r") as f:
        schemamap = json.load(f)
    return schemamap

def map_ner(doc_dat):
    """
    Maps any NER class name to "ENTITY"
    """
    new_ner = []
    for ner_list in doc_dat['ner']:
        new_ner_list = []
        for ner in ner_list:
          ner[2] = "ENTITY"
          new_ner_list.append(ner)
        new_ner.append(new_ner_list)
    doc_dat['ner']  = new_ner

def map_relation(doc_dat,schemamap):
    """
    Maps relation classes to new schema given by dict
    """
    new_rel = []
    for rel_list in doc_dat['relations']:
        new_rel_list = []
        rel_list = [rel for rel in rel_list if rel[4] in schemamap]
        for rel in rel_list:
            rel[4] = schemamap[rel[4]]
            new_rel_list.append(rel)
        if len(new_rel_list):
            new_rel.append(new_rel_list)
    doc_dat['relations'] =  new_rel

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataroot', type=str, default='/net/nfs2.corp/s2-research/tomh/UnifiedData', help='root dir for dataset folders')
    parser.add_argument('--dataset', type=str, choices = ['scierc','gold_covid','chemprot','srl'], default='chemprot', help='which dataset to map')
    parser.add_argument('--maptype', choices = ['mech','mech_effect'],default="mech", help='if specified, will download all files from s3 for given release date')

    args = parser.parse_args()
    
    root_path = Path(args.dataroot)
    dataset_dir = root_path / args.dataset
    original_dir = dataset_dir / "original"
    map_dir = dataset_dir / "mapped"

    map_type = args.maptype
    map_path = map_dir.joinpath(map_type+".txt")

    schemamap = load_map_dict(map_path)   
    original_files = [path for path in original_dir.glob('*.jsonl')]

    print("--- loading and mapping from ", original_dir)
    for fold in original_files:
        print(fold.name)
        fold_mapped_dir = map_dir.joinpath(map_type)
        Path(fold_mapped_dir).mkdir(parents=True, exist_ok=True)
        fold_mapped = fold_mapped_dir/fold.name
        new_jsons = []
        with jsonlines.open(fold,'r') as reader:
            for obj in tqdm(reader):
                map_ner(obj)
                map_relation(obj,schemamap)
                new_jsons.append(obj)

        with jsonlines.open(fold_mapped, 'w') as writer:
            writer.write_all(new_jsons)
        
# def read_refine_labels(data_path, filename, output_filename):
#   input_file = open(data_path + filename)
#   output_file = open(data_path + output_filename, "w")
#   for line in input_file:
#     data = json.loads(line)
    
#     #replacing ner
#     new_ner = []
#     for ner_list in data['ner']:
#       new_ner_list = []
#       for ner in ner_list:
#         if SCIERC_NER_REPLACEMENT[ner[2]] != -1:
#           ner[2] = SCIERC_NER_REPLACEMENT[ner[2]]
#           new_ner_list.append(ner)
#       new_ner.append(new_ner_list)
#     data['ner']  = new_ner

#     # replacing rel
#     new_rel = []
#     for rel_list in data['relations']:
#       new_rel_list = []
#       for rel in rel_list:
#         if SCIERC_REL_REPLACEMENT[rel[4]] != -1:
#           rel[4] = SCIERC_REL_REPLACEMENT[rel[4]]
#           new_rel_list.append(rel)
#       new_rel.append(new_rel_list)
#     data['relations']  = new_rel
#     json.dump(data, output_file)
#     output_file.write('\n')

# def merge_data():
#   srl_data = read_refine_labels(SCIERC_PATH, "train.scierc.jsonl", "train.scierc.unified.jsonl")
#   srl_data = read_refine_labels(SCIERC_PATH, "dev.scierc.jsonl", "dev.scierc.unified.jsonl")
#   srl_data = read_refine_labels(SCIERC_PATH, "test.scierc.jsonl", "test.scierc.unified.jsonl")
# merge_data()