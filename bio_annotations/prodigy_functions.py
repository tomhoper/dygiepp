import pathlib
from pathlib import Path
import json
import argparse
import utils as ut
import dataset_creator as dc
import os.path
from os import path

CORRECTION_DIR_PATH = "corrections/jsons/"
ANNOTATION_DIR_PATH = "annotations/jsons/"
NEEDED_CORRECTION_INDEX_PATH = "correction_indexes/"
DEFAULT_LIST = ["sara", "megan", "madeline", "kristina", "jeff"]

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
    correction_path = CORRECTION_DIR_PATH + "corrections_" + annotator_name + '.jsonl'
    if annotator_name == "tom":
        correction_path = CORRECTION_DIR_PATH + "corrections_" + annotator_name + '_NEW.jsonl'
    if path.exists(correction_path):
      correction_data = ut.read_data_base(correction_path, annotator_name)
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
      # print(correction_other)
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
    already_annotated_list = ut.read_already_annotated(["ner_rels_bio_tom_correction_NEW"])
    print("already_annotated_list")
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

def update_annotations_corrections():
    ut.update_extractions(ut.DEFAULT_NAME_LIST, ut.ANNOTATION_DIR_PATH, annotations_correction="annotations")
    ut.update_extractions(ut.DEFAULT_CORRECTION_NAME_LIST, ut.CORRECTION_DIR_PATH, annotations_correction="correction")
    ut.merge_with_old(ut.ANNOTATION_DIR_PATH + "jsons/", ut.ANNOTATION_DIR_PATH_OLD + 'jsons/')
    ut.merge_with_old(ut.CORRECTION_DIR_PATH + "jsons/", ut.CORRECTION_DIR_PATH_OLD + 'jsons/')

    for name in ut.DEFAULT_NAME_LIST:
        annotation_name = 'annotations_' + name + '.jsonl'
        annotation_name_tsv = 'annotations_' + name + '.tsv'
        annotation_json_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "jsons" / annotation_name
        annotation_tsv_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "tsvs" / annotation_name_tsv
        # ut.visualize_the_annotations_to_tsv(annotation_json_file, annotation_tsv_file)
    for name in ut.DEFAULT_CORRECTION_NAME_LIST:
        annotation_name = 'corrections_' + name + '.jsonl'
        annotation_name_tsv = 'corrections_' + name + '.tsv'
        correction_json_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "jsons" / annotation_name
        correction_tsv_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "tsvs" / annotation_name_tsv
        # ut.visualize_the_annotations_to_tsv(correction_json_file, correction_tsv_file)

def write_annotations_for_tom(input_filename):
    input_file = open(input_filename)
    key_text_pair_seen = ('','')
    relation_info = []
    count = 0 # to add the lines more than 274
    already_annotated_list = ut.read_already_annotated(["ner_rels_bio_tom_correction"])
    print(len(already_annotated_list))
    output_file = open("tom_curation_file.jsonl", "w")
    seen_list = [0 for x in range(len(already_annotated_list))]
    edit_needed = False
    for line in input_file:
        count += 1
        # import pdb; pdb.set_trace()
        doc_id, text, arg0, arg1, rel, accept, _, edit, comment = line.split('\t')[:9]
        if accept == "reject":
            continue
        if (doc_id, text) != key_text_pair_seen:
            if key_text_pair_seen != ('',''):
                res = ut.convert_to_json(key_text_pair_seen[1], relation_info, key_text_pair_seen[0])
                if (edit_needed or count > 273) and (key_text_pair_seen[0], key_text_pair_seen[1]) not in already_annotated_list:
                    json.dump(res, output_file)
                    output_file.write('\n')
            relation_info = []
            edit_needed = False
            if edit != '':
                edit_needed = True
            key_text_pair_seen = (doc_id, text)
            relation_info.append((rel, arg0, arg1))
        else: 
            if edit != '':
                edit_needed = True
            relation_info.append((rel, arg0, arg1))

    res = ut.convert_to_json(key_text_pair_seen[1], relation_info, key_text_pair_seen[0])
    if (edit_needed or count > 273) and (key_text_pair_seen[0], key_text_pair_seen[1]) not in already_annotated_list:
        json.dump(res, output_file)
        output_file.write('\n')
    import pdb; pdb.set_trace()




if __name__ == "__main__":
  parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

  parser.add_argument('--name',
                      type=str,
                      default="madeline",
                      help='annotator name, comma seperated',
                      required=False)
  parser.add_argument('--others',
                      type=str,
                      default="megan,sara,madeline",
                      help='other annotator\' names for validations, comma seperated',
                      required=False)
  
  parser.add_argument('--command_type',
                      type=str,
                      default="megan,sara,madeline",
                      help='Please select one of the following options \n \
                            annotator_stat --> get the data and stats of one specific person annotations\n \
                            self_correction --> get the correction file for a annotator\n \
                            rel-validation --> get validation for one person from other people\'s annotations in relation level\n \
                            par-validation--> get validation for one person from other people\'s annotations in relation level\n \
                            prodigy-json-by-tsv --> converts the tsv file to the prodigy formatted json \n \
                            all-data --> get all the dataset annotated ready \n\
                            prodigy-upload --> get the port and data and runs the command to load the annotation site(please set flag for correction or validation to load those data or give the datafile directly',
                      required=True)

  parser.add_argument('--annotated_path',
                        type=str,
                        default="corrections/tsvs/corrections_tom.tsv",
                        help='path to final set of annotations',
                        required=False)

  parser.add_argument('--root',
                        type=str,
                        default="/data/aida/covid_clean/",
                        help='path to complete set of annotations',
                        required=False)

  parser.add_argument('--correction',
                        action='store_true')

  parser.add_argument('--validation',
                        action='store_true')

  parser.add_argument('--input_filename',
                      type=str,
                      default="",
                      help='The input file name for loading prodigy link(if not given the default values will be used)',
                      required=False)

  parser.add_argument('--port',
                      type=str,
                      default="2222",
                      help='The port number to run prodigy annotation link on ',
                      required=False)


  parser.add_argument('--annotations_path',
                      type=str,
                      default="data/covid/json/bio_annotations",
                      help='where to save the path to merged annotations',
                      required=False)
  args = parser.parse_args()

  if args.command_type == "annotator_stat":
    write_all_annotations(args.name)
  elif args.command_type == "self_correction":
    create_correction_input(args.name)
  elif args.command_type == "rel-validation":
    print("TODO")
  elif args.command_type == "prodigy-upload":
      input_filename = ""
      db_name = ""
      # findin the input file name for the link
      if args.input_filename != "":
        input_filename = args.input_filename
      else:
        if args.validation == True:
          input_filename = "validation_input_" + args.name + ".jsonl"
        elif args.correction == True:
          input_filename = "correction_input_" + args.name + '.jsonl'
        else:
          input_filename = 'input_' + args.name + '.jsonl'
  
      db_name = "ner_rels_bio_" + args.name
      if args.validation == True or args.correction == True:
        db_name = db_name + '_correction'
        if args.name == "tom":  #since the name was changed
          db_name = db_name + "_NEW"

      ut.run_prodigy_command(input_filename, db_name, args.port)

  elif args.command_type == "par-validation":
      if args.others == "":
          print("Error: we need a list of people to validate, switching to default list of " + str(DEFAULT_LIST))
          args.others = DEFAULT_LIST
      else:
        args.others = args.others.split(",")
      create_validation_input(args.name, args.others)
  elif args.command_type == "all-data":
      ut.update_extractions(["tom"], ut.CORRECTION_DIR_PATH, annotations_correction="correction")

      annotation_name = 'corrections_tom.jsonl'
      annotation_name_tsv = 'corrections_tom.tsv'
      correction_json_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "jsons" / annotation_name
      correction_tsv_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "tsvs" / annotation_name_tsv
      dataset = ut.read_data_base(correction_json_file, annotator_name="tom")
      ut.visualize_the_annotations_to_tsv(dataset, correction_tsv_file)

      test_keys, dev_keys = dc.get_test_indexes(args.annotated_path)
      dc.create_annotated_covid(True, args.root, args.annotated_path, test_keys, dev_keys)
      print('mech only data created')
      dc.create_annotated_covid(False, args.root, args.annotated_path, test_keys, dev_keys)
      print('mech effect data created')
      dc.write_gold_file(True, args.root, args.annotated_path, test_keys)
      print('mech only gold created')

      dc.write_gold_file(False, args.root, args.annotated_path, test_keys)
      print('mech effect gold created')
