import argparse
import random
import json
import copy

random.seed(100)

def remove_repetition(data_list):
  pruned_data = []
  doc_key_list = []
  for data in data_list:
      doc_key = data['meta']['doc_key']
      text = data['text']
      if (doc_key, text) not in doc_key_list:
        doc_key_list.append((doc_key, text))
        pruned_data.append(data)
  return pruned_data

def read_data_base(database_filename, annotator_name):
  data_list = [] 
  db_file = open(database_filename)
  for line in db_file:
      data = json.loads(line)
      data['annotator'] = annotator_name
      data_list.append(data)
  return data_list

def visualize_the_annotations_to_tsv(data_list, output_tsv_file_name):
    output_tsv_file = open(output_tsv_file_name, 'w')
    # output_tsv_file.write("doc_key\ttext\thead\tchild\tlabel\t\taccept_reject\n")
    pruned_data = []
    for data in data_list:
        doc_key = data['meta']['doc_key']
        answer = data['answer']
        text = data['text']
        if answer == "reject":
            # output_tsv_file.write(doc_key + '\t' + text + '\t\t\t\treject\n')
            continue
        elif answer == "ignore":
          continue
        pruned_data.append(data)
        for i in range(len(data['relations'])):
          relations_head = text[data['relations'][i]['head_span']['start']:data['relations'][i]['head_span']['end']]
          relations_child = text[data['relations'][i]['child_span']['start']:data['relations'][i]['child_span']['end']]
          relation_label = data['relations'][i]['label']
          output_tsv_file.write(doc_key + '\t' + text + '\t' + relations_head + '\t' + relations_child + '\t' + relation_label + '\taccept\n')
    return pruned_data


def make_single_vaidation_row_prediction(complete_data_list, output_file_name):
  output_file = open(output_file_name, "w")
  final_list = []
  random.shuffle(complete_data_list)
  for data in complete_data_list:
    for i in range(len(data['relations'])):
      new_data = copy.deepcopy(data)
      # import pdb; pdb.set_trace() 
      new_data['relations'] = []
      new_data['relations'].append(data['relations'][i])
      json.dump(new_data, output_file)
      output_file.write("\n")



if __name__ == "__main__":
  parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

  parser.add_argument('--names',
                      type=str,
                      default="kristina,jeff,megan",
                      help='annotator names, comma seperated',
                      required=False)
  parser.add_argument('--annotations_path',
                      type=str,
                      default="data/covid/json/bio_annotations",
                      help='where to save the path to merged annotations',
                      required=False)
  args = parser.parse_args()


  complete_data_list = []
  name_list = args.names.split(',')
  for name in name_list:
    data_list = read_data_base("annotations_" + name+ ".jsonl", name)
    data_list = remove_repetition(data_list)
    complete_data_list = complete_data_list + data_list
  make_single_vaidation_row_prediction(complete_data_list, "validate.jsonl")
