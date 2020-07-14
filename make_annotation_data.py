import json
import random
random.seed(100)

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

def create_annotation_data(input_filename, output_filename):
  # import pdb; pdb.set_trace()
  input_file = open(input_filename)
  
  output_res = []
  data_list = []
  for line in input_file:
    data_list.append(json.loads(line))
  random.shuffle(data_list)
  common_annotations = []
  for i in range(1,10):
    output_res = []
    # if i > 1:
    #   for r in common_annotations:
    #     output_res.append(r)
    print(i)
    output_file = open(output_filename + str(i) + '.jsonl', 'w')
    data_list_part = data_list[i*100:(i+1)*100]
    for j in range(len(data_list_part)):
      data = data_list_part[j]
      res = get_info_from_data_partitioned(data)
      for r in res:
          # import pdb; pdb.set_trace()
          # if j < 10 and i == 1:
          #   common_annotations.append(r)
          output_res.append(r)
    # data_list.append(get_info_from_data(data))
    for data in output_res:
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
    


# create_annotation_data("../dygiepp/data/covid/json/test_abstracts_50k_valid_removed.json", "bio_selected_t")

find_the_val_train_index_list("../dygiepp/data/covid/json/test_abstracts_50k_valid_removed.json")



