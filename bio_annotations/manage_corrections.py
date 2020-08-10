import json
import argparse
import utils as ut
import os.path
from os import path

CORRECTION_DIR_PATH = "corrections/jsons/"
ANNOTATION_DIR_PATH = "annotations/jsons/"
NEEDED_CORRECTION_INDEX_PATH = "correction_indexes/"
DEFAULT_NAME_LIST = ["madeline", "megan", "sara", "yeal"]

def read_correction_indexes(index_filename):
    if not path.exists(index_filename):
      return []
    res_indexes = []
    input_file = open(index_filename)
    for line in input_file:
      if line[:-1] not in res_indexes:
        res_indexes.append(line[:-1])
    print("count of corrections that are needed is " + str(len(res_indexes)))
    return res_indexes

def create_correction_input(annotator_name, full_mode=False):
    #add the annotations that are not corrected + correction indexes(all if full mode == true) 
    output_file = open("correction_input_" + annotator_name + ".jsonl", "w")
    print("creating file " + "correction_input_" + annotator_name + ".jsonl")
    annotation_data = ut.read_data_base(ANNOTATION_DIR_PATH + "annotations_" + annotator_name + '.jsonl', annotator_name)
    correction_data = []
    if path.exists(CORRECTION_DIR_PATH + "corrections_" + annotator_name + '.jsonl'):
      correction_data = ut.read_data_base(CORRECTION_DIR_PATH + "corrections_" + annotator_name + '.jsonl', annotator_name)
    correction_indexes = read_correction_indexes(NEEDED_CORRECTION_INDEX_PATH + annotator_name + '.txt')

    correction_key_version_map = {}
    for item in correction_data:
      doc_key = item['meta']['doc_key'].split('_::_')
      if len(doc_key) == 1:
        time_index = 0
      else:
        time_index = int(doc_key[1])
      if doc_key[0] in correction_key_version_map:
        if correction_key_version_map[doc_key[0]] < time_index:
            correction_key_version_map[doc_key[0]] = time_index
      else:
        correction_key_version_map[doc_key[0]] = time_index

    if full_mode == True:
      seen_keys = []
      for item in correction_data:
        doc_key = item['meta']['doc_key'].split('::')
        if doc_key[0] in seen_keys:
          continue
        else:
          item['meta']['doc_key'] = doc_key[0] + "::" + str(correction_key_version_map[doc_key[0]] + 1)
          json.dump(item, output_file)
          output_file.write("\n")
    else:
      for correction_key in  correction_indexes:
        for item in correction_data:
          doc_key = item['meta']['doc_key'].split('::')
          if doc_key[0] != correction_key:
            continue
          else:
            item['meta']['doc_key'] = doc_key[0] + "::" + str(correction_key_version_map[doc_key[0]] + 1)
            del item['_task_hash']
            del item['_input_hash']
            # item['tokens'].append("::" + str(correction_key_version_map[doc_key[0]] + 1))
            item['text'] = item['text'] + " ::v" + str(correction_key_version_map[doc_key[0]] + 1)

            json.dump(item, output_file)
            output_file.write("\n")


    correction_data = []
    if path.exists(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl'):
      correction_data = ut.read_data_base(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl', annotator_name)
    correction_doc_keys = []

    for item in correction_data:
      correction_doc_keys.append((item['meta']['doc_key'], item['text']))
    count = 0
    print(len(annotation_data))
    print(len(correction_doc_keys))
    annotation_doc_keys = []
    for item in annotation_data:   #Writing the annotations that are not corrected yet
      if (item['meta']['doc_key'], item['text']) not in correction_doc_keys:
        count += 1
        json.dump(item, output_file)
        output_file.write("\n")
    print(count)

def get_latest_correction_version(correction_data):
  #there might be multiple rounds of corrections and we want the latest ones.
  correction_key_version_map = {}
  for item in correction_data:
        doc_key = item['meta']['doc_key'].split('_::_')
        if len(doc_key) == 1:
          time_index = 0
        else:
          time_index = int(doc_key[1])
        if doc_key[0] in correction_key_version_map:
          if correction_key_version_map[doc_key[0]] < time_index:
              correction_key_version_map[doc_key[0]] = time_index
        else:
          correction_key_version_map[doc_key[0]] = time_index
  return correction_key_version_map

def divide_self_other_correction(annotated_data, corrected_data):
    validation_data = []
    self_correction_data = []
    annotation_doc_keys = get_list_of_ids(annotated_data)
    for item in corrected_data:
      if (item['meta']['doc_key'], item['text']) not in annotation_doc_keys:
        self_correction_data.append(item)
      else:
        validation_data.append(item)
    return validation_data, self_correction_data

def get_list_of_ids(data_list):
  # returning all unique pairs of (doc_key, text) per dataset
  doc_keys = []
  for item in data_list:
    if (item['meta']['doc_key'].split('_::_')[0], item['text']) not in doc_keys:
      doc_keys.append((item['meta']['doc_key'].split('_::_')[0], item['text']))
  return doc_keys

def write_all_annotations(name_list):
    seen_keys = []
    #counting all unique corrections and non-corrected annotations per person
    doc_key_list = []
    conmplete_set = []
    annotation_count = 0
    correction_count = 0
    validation_count = 0
    for name in name_list:
      print ("reading annotation for : " + name)

      annotation_other =  ut.read_data_base(ANNOTATION_DIR_PATH + "annotations_" + name + '.jsonl', name)
      correction_other = []
      if path.exists(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl'):
        correction_other = ut.read_data_base(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl', name)
    
      correction_key_version_map = get_latest_correction_version(correction_other)

      validation_data, corrected_data = divide_self_other_correction(annotation_other, correction_other)
      self_correction_doc_keys = get_list_of_ids(corrected_data)
      validation_doc_keys = get_list_of_ids(validation_data)

      for item in correction_other:
        if (item['meta']['doc_key'], item['text']) in seen_keys:
          continue
        seen_keys.append((item['meta']['doc_key'], item['text']))
        doc_key = item['meta']['doc_key'].split('_::_')
        if len(doc_key) == 1 or (int(doc_key[1]) == correction_key_version_map[doc_key[0]]):
          conmplete_set.append(item)
          if (item['meta']['doc_key'], item['text']) in self_correction_doc_keys:
            correction_count += 1
          else:
            validation_count += 1

      correction_doc_keys = get_list_of_ids(correction_other)
      
      for item in annotation_other:
        if (item['meta']['doc_key'], item['text']) not in correction_doc_keys:
          annotation_count += 1
          conmplete_set.append(item)

    ut.visualize_the_annotations_to_tsv(conmplete_set, "annotated_complete_"+name+ ".tsv")
    ut.visualize_the_annotations_to_tsv(validation_data, "validation_"+name+ ".tsv")

    print("correction_count" + str(correction_count))
    print("annotation_count" + str(annotation_count))
    print("validation_count" + str(validation_count))
    return conmplete_set


def create_validation_input(annotator_name, others_namelist):
    #add the annotations that are not corrected + correction indexes(all if full mode == true) 
    output_file = open("validation_input_" + annotator_name + ".jsonl", "w")
    seen_annotations= []
    print("creating file " + "correction_input_" + annotator_name + ".jsonl")
    validation_data = []
    for name in others_namelist:
      print ("reading corrections and annotations for " + name)

      annotation_other =  ut.read_data_base(ANNOTATION_DIR_PATH + "annotations_" + name + '.jsonl', name)
      correction_other = []
      if path.exists(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl'):
        correction_other = ut.read_data_base(CORRECTION_DIR_PATH + "corrections_" + name + '.jsonl', name)
    
      correction_key_version_map = get_latest_correction_version(correction_other)
      print(correction_other)
      for item in correction_other:
        doc_key = item['meta']['doc_key'].split('_::_')
        if item['answer'] == "reject" or item['answer'] == 'ignore':
          continue
        if len(doc_key) == 1 or (int(doc_key[1]) == correction_key_version_map[doc_key[0]]):
          validation_data.append(item)

      correction_doc_keys = get_list_of_ids(correction_other)

      for item in annotation_other:
        if item['answer'] == "reject" or item['answer'] == 'ignore':
          continue
        if (item['meta']['doc_key'], item['text']) not in correction_doc_keys:
          if( item['meta']['doc_key'], item['text'] )not in seen_annotations:
            validation_data.append(item)
            seen_annotations.append( (item['meta']['doc_key'], item['text']) )

      print("validation data count so far : " + str(len(validation_data)))
      print("validation data count so far : " + str(len(annotation_other)))
    
    for item in validation_data:
      json.dump(item, output_file)
      output_file.write("\n")

def make_correction_data(data_list, output_file_name):
  output_file  = open(output_file_name, "w")
  for data in data_list:
      json.dump(data, output_file)
      output_file.write("\n")

def write_annotations_for_tom_jsonl(complete_set):
    already_annotated_list = ut.read_already_annotated(["ner_rels_bio_tom_correction"])
    print(len(already_annotated_list))
    output_file = open("tom_curation2_file.jsonl", "w")
    count = 0
    seen_list = [0 for x in range(len(already_annotated_list))]
    for data in complete_set:
      doc_key = data['meta']['doc_key']
      answer = data['answer']
      text = data['text']
      if answer == "accept" and len(data['relations']) == 0:
        count += 1
      if answer == "accept" and len(data['relations']) > 0 and (doc_key, text) not in already_annotated_list:
        json.dump(data, output_file)
        output_file.write('\n')
    print(count)



if __name__ == "__main__":
  parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

  parser.add_argument('--names',
                      type=str,
                      default="megan,sara,madeline",
                      help='annotator names, comma seperated',
                      required=False)
  parser.add_argument('--annotations_path',
                      type=str,
                      default="data/covid/json/bio_annotations",
                      help='where to save the path to merged annotations',
                      required=False)
  args = parser.parse_args()
  if args.names != "":
    name_list = args.names.split(',')
  else:
    name_list = DEFAULT_NAME_LIST
  # print(name_list)

# "bxxw0eey_abstract"

  # ut.run_prodigy_command("bio_selected8.jsonl", "ner_rels_bio_aida", 5020)
  # ut.update_extractions(["aida"], "annotations/")
  # for name in name_list:
  #   create_correction_input(name, full_mode=False)
  data = write_all_annotations(["madeline"])
  write_annotations_for_tom_jsonl(data)
  # create_validation_input("tom_jeff", ["jeff"])
  # create_validation_input("tom_kristina", ["kristina"])








