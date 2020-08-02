import json
import random
from os import listdir
from os.path import isfile, join
import pathlib
from pathlib import Path
import utils as ut

random.seed(100)
ANNOTATED_FILEPATH = "annotations/"
NAME_LIST  = ["megan", "madeline", "kristina", "jeff", "sara", "yeal"]


def get_info_from_data(data):
  output = {}
  text = ""
  for i in range(len(data["sentences"])):
    text = text + " ".join(data["sentences"][i])+ ' '
  text = text[:-1]
  output["text"] = text
  metadata = {}
  metadata["section"] = data["section"]
  metadata["doc_key"] = data["doc_key"]
  output["meta"] = metadata
  return output

def get_info_from_data_partitioned(data):
  output_list = []
  output = {}
  text = ""
  len_sum = 0
  for i in range(len(data["sentences"])):
    if len(data["sentences"][i]) + len_sum > 50:
          output["text"] = text[:-1]
          metadata = {}
          metadata["section"] = data["section"]
          metadata["doc_key"] = data["doc_key"]
          output["meta"] = metadata
          output_list.append(output)
          text = ""
          len_sum = 0
          output = {}
    len_sum += len(data["sentences"][i])
    text = text + " ".join(data["sentences"][i])+ ' '
  text = text[:-1]
  output["text"] = text
  metadata = {}
  metadata["section"] = data["section"]
  metadata["doc_key"] = data["doc_key"]
  output["meta"] = metadata
  output_list.append(output)
  return output_list

def check_alread_annotated(allread_annotated_list, datapoint):

    if (datapoint['meta']['doc_key'], datapoint['text']) not in allread_annotated_list:
      return True
    return False


def create_annotation_data(input_filename, output_filename):
    # ut.update_extractions(NAME_LIST, ANNOTATED_FILEPATH)
    already_annotated = find_already_annotated()  
    # anotator_already_annotated = find_already_annotated_by_annotator("sara")  
    # anotator_already_annotated = find_already_annotated_by_annotator("megan")  
    anotator_already_annotated = find_already_annotated_by_annotator("yeal")  
    # anotator_already_annotated = find_already_annotated_by_annotator("madeline")  
    annotator_abstract_id_text = []
    print(len(anotator_already_annotated))
    already_annotated_abstract_id_text = []

    for item in already_annotated:
      already_annotated_abstract_id_text.append((item['meta']['doc_key'], item['text']))

    for item in anotator_already_annotated:
      annotator_abstract_id_text.append((item['meta']['doc_key'], item['text']))

    input_file = open(input_filename)    
    output_res = []
    data_list = []

    for line in input_file:
      data_list.append(json.loads(line))
    
    random.shuffle(data_list)
    common_annotations = []
    common_data = []
    for i in range(0,10):
      output_res = []
      

      print(i)
      output_file = open(output_filename + str(i) + '.jsonl', 'w')
      data_list_part = data_list[i*100:(i+1)*100]
      for j in range(len(data_list_part)):
        data = data_list_part[j]
        res = get_info_from_data_partitioned(data)
        for r in res:
            # import pdb; pdb.set_trace()
            if j < 10 and i == 1:
              # import pdb; pdb.set_trace()
              if check_alread_annotated(annotator_abstract_id_text, r) == False:
                print("here")
                continue
              common_annotations.append(r)
            output_res.append(r)
      common_data_written = False
      for data in output_res:
        if check_alread_annotated(already_annotated_abstract_id_text, data) == False:
          continue
        if common_data_written == False and i > 1:
          common_data_written = True
          for d in common_annotations:
            json.dump(d, output_file)
            output_file.write("\n")
        json.dump(data, output_file)
        output_file.write("\n")

    # import pdb; pdb.set_trace()
    for i in range(10,20):
      output_res = []
      print(i)
      output_file = open(output_filename + str(i) + '.jsonl', 'w')
      data_list_part = data_list[i*200:(i+1)*200]
      for j in range(len(data_list_part)):
        data = data_list_part[j]
        res = get_info_from_data_partitioned(data)
        for r in res:
            # import pdb; pdb.set_trace()
            output_res.append(r)
      common_data_written = False
      for data in output_res:
        if check_alread_annotated(already_annotated_abstract_id_text, data) == False:
          continue
        if common_data_written == False and i > 1:
          common_data_written = True
          for d in common_annotations:

            json.dump(d, output_file)
            output_file.write("\n")
        json.dump(data, output_file)
        output_file.write("\n")  

def find_the_val_train_index_list(input_filename):
  input_file = open(input_filename)
  data_list = []
  output_train_file = open("test_abstracts_50k_valid_removed_annotations.jsonl", "w")
  output_val_file = open("validation_bio_with_annotations.jsonl", "w")
  for line in input_file:
    data_list.append(json.loads(line))
  random.shuffle(data_list)
  output_file_train_indexes = open("train_indexe.txt","w")
  for i in range(1000, len(data_list)):
    output_file_train_indexes.write(data_list[i]["doc_key"] + '\n')
  for i in range(1000):
    json.dump(data_list[i], output_val_file)
    output_val_file.write('\n')
  for i in range(1000, len(data_list)):
    json.dump(data_list[i], output_train_file)
    output_train_file.write('\n')
    
def find_already_annotated():
    res_list = []
    annotation_path =  pathlib.Path(ANNOTATED_FILEPATH) / "jsons"  
    onlyfiles = [f for f in listdir(str(annotation_path)) if (isfile(join(str(annotation_path), f)) and f.endswith('jsonl'))]
    for file in onlyfiles:
        print(file)
        annotator_name = file.split('.')[0]
        res_list = res_list + ut.read_data_base(join(str(annotation_path), file), annotator_name)
    return res_list

def find_already_annotated_by_annotator(name):
    res_list = []
    annotation_path =  pathlib.Path(ANNOTATED_FILEPATH) / "jsons"  
    onlyfiles = [f for f in listdir(str(annotation_path)) if (isfile(join(str(annotation_path), f)) and f.endswith('jsonl'))]
    for file in onlyfiles:
        if name not in file:
          continue
        print(file)
        annotator_name = file.split('.')[0]
        res_list = res_list + ut.read_data_base(join(str(annotation_path), file), annotator_name)
    return res_list





create_annotation_data("../data/covid/json/test_abstracts_50k_valid_removed.json", "bio_selected")

# find_the_val_train_index_list("../dygiepp/data/covid/json/test_abstracts_50k_valid_removed.json")



