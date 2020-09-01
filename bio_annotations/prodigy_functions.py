import pathlib
from pathlib import Path
import json
import argparse
import utils as ut
import dataset_creator as dc
import kesafatkari as ks
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
                            prodigy-json-by-tsv-rels --> converts the tsv file to the prodigy formatted json (each relastion to one input) \n \
                            all-data --> get all the dataset annotated ready \n\
                            after-stiching-tom --> get all the data and combine them for a final jsonl/tsv for tom \n\
                            prodigy-upload --> get the port and data and runs the command to load the annotation site(please set flag for correction or validation to load those data or give the datafile directly',
                            
                      required=True)

  parser.add_argument('--annotated_path',
                        type=str,
                        default="corrections/tsvs/corrections_tom.tsv",
                        help='path to final set of annotations',
                        required=False)

  parser.add_argument('--output_data_name',
                        type=str,
                        default="s_final",
                        help='path to final set of annotations',
                        required=False)

  parser.add_argument('--root',
                        type=str,
                        default="/data/aida/covid_aaai/",
                        help='path to complete set of annotations',
                        required=False)

  parser.add_argument('--needs_update',
                        action='store_true')

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

  elif args.command_type == "prodigy-json-by-tsv":
    input_file = open(args.annotated_path)
    key_text_pair_seen = []
    relation_info = []
    output_file = open(args.output_data_name, "w")
    data_list = []
    for line in input_file:
        # import pdb; pdb.set_trace()
        doc_id, text, arg0, arg1, rel, _ = line[:-1].split('\t')[:6]
        data_list.append([doc_id, text, arg0, arg1, rel])
    for item in data_list:
        doc_id, text, arg0, arg1, rel = item
        if (doc_id, text) not in key_text_pair_seen:
          relation_info = []
          relation_info.append((rel, arg0, arg1))
          key_text_pair_seen.append((doc_id, text))
          for other in data_list:
            other_doc_id, other_text, other_arg0, other_arg1, other_rel = other
            if item == other:
              continue
            if (doc_id, text) == (other_doc_id, other_text):
              relation_info.append((other_rel, other_arg0, other_arg1))
          res = ut.convert_to_json(text, relation_info, doc_id)
          json.dump(res, output_file)
          output_file.write('\n')


  elif args.command_type == "prodigy-json-by-tsv-rels":
    input_file = open(args.annotated_path)
    key_text_pair_seen = []
    relation_info = []
    output_file = open(args.output_data_name, "w")
    data_list = []
    for line in input_file:
        # import pdb; pdb.set_trace()
        doc_id, text, arg0, arg1, rel, _ = line[:-1].split('\t')[:6]
        data_list.append([doc_id, text, arg0, arg1, rel])
    for item in data_list:
        doc_id, text, arg0, arg1, rel = item
        relation_info = []
        relation_info.append((rel, arg0, arg1))
        res = ut.convert_to_json(text, relation_info, doc_id)
        json.dump(res, output_file)
        output_file.write('\n')

  elif args.command_type == "par-validation":
      if args.others == "":
          print("Error: we need a list of people to validate, switching to default list of " + str(DEFAULT_LIST))
          args.others = DEFAULT_LIST
      else:
        args.others = args.others.split(",")
      create_validation_input(args.name, args.others)
  elif args.command_type == "all-data":
      if args.needs_update:
        ut.update_extractions(["tom"], ut.CORRECTION_DIR_PATH, annotations_correction="correction")

        annotation_name = 'corrections_tom.jsonl'
        annotation_name_tsv = 'corrections_tom.tsv'
        correction_json_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "jsons" / annotation_name
        correction_tsv_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "tsvs" / annotation_name_tsv
        dataset = ut.read_data_base(correction_json_file, annotator_name="tom")
        ut.visualize_the_annotations_to_tsv(dataset, correction_tsv_file)

      test_keys, dev_keys = dc.get_test_indexes(args.annotated_path)
      test_keys = ['ipmyfxk5_abstract', '1x1bnt5j_abstract', 'yfyd2ysn_abstract', 'tot67l0j_abstract', '7lf2c2ra_abstract', 'w8trclz6_abstract', 'v6f3c6ep_abstract', '43h1r4pm_abstract', 'afce61g0_abstract', '4y05t72c_abstract', '75dzc62b_abstract', 'rvxxeg32_abstract', 's4g3awyc_abstract', 'u2jky7gl_abstract', 'tt761tte_abstract', '84tvi1gb_abstract', 'tl2seigh_abstract', 'e2r38v29_abstract', 'oc90ec5v_abstract', 'ljzfyz37_abstract', 'tbbe54ue_abstract', 'xfnbv6o9_abstract', 'a1xy2k6s_abstract', 'ey040q2l_abstract', 'm7s39je2_abstract', '7rgk946s_abstract', 'kcm86l15_abstract', 'mjp6uyqz_abstract', 'll6lkhyd_abstract', 'hxlebas8_abstract', 'rs54zugh_abstract', 'q5mgue5z_abstract', 'puezkbza_abstract', 'bfw8ys04_abstract', 'xkfcc2dx_abstract', '70wp8n0d_abstract', 'clo5qzcz_abstract', '2jhxnape_abstract', 'u9svz7pf_abstract', '4213xdfk_abstract', '0mzzyih0_abstract', 'wfkk7dsm_abstract', 'bsz4va3o_abstract', 'bom4rhsh_abstract', 'xhdub3br_abstract', '4ijrdkxe_abstract', 'yj2kunat_abstract', 'z15j8izi_abstract', 'fexy2p6h_abstract', '31v9gvd8_abstract']
      dev_keys = ['655polth_abstract', 'atj3fad6_abstract', 'azzgygzk_abstract', 'n6wz3rvb_abstract', '0n1pea70_abstract', '8mnfx8wo_abstract', 'dqeci7lc_abstract', '0b06zk1q_abstract', '58p5b2vw_abstract', 'z3v89zsx_abstract', 'fpsyem7x_abstract', '4r0t3q7j_abstract', 'zr3q5rd7_abstract', 'dif6czi2_abstract', 'w0lfgajt_abstract', 'wekvet6f_abstract', 'iomao9a7_abstract', 'ohq0i87o_abstract', '86srlles_abstract', 'y8o5j2be_abstract', 'rvp7xt2n_abstract', '0j4ot2rn_abstract', 'es7b1rs0_abstract', '8n2s0bl1_abstract', 'jtmokwgu_abstract', 'nmt221tu_abstract', '59sibx6a_abstract', 'ea2cty58_abstract', 'r847zzv9_abstract', '30d7t5bf_abstract']
      dc.create_annotated_covid(True, args.root, args.annotated_path, test_keys, dev_keys, args.output_data_name)
      print('mech only data created')
      dc.create_annotated_covid(False, args.root, args.annotated_path, test_keys, dev_keys, args.output_data_name)
      print('mech effect data created')
      dc.write_gold_file(True, args.root, args.annotated_path, test_keys, args.output_data_name)
      print('mech only gold created')

      dc.write_gold_file(False, args.root, args.annotated_path, test_keys, args.output_data_name)
      print('mech effect gold created')
      dc.write_gold_file(False, args.root, args.annotated_path, dev_keys, "dev_" + args.output_data_name)
      dc.write_gold_file(True, args.root, args.annotated_path, dev_keys, "dev_" + args.output_data_name)
 

  elif args.command_type == "after-stiching-tom":
      # combining the partitions that are already correct + getting data from updated stiching and combine
      # get updated stiching dataset:
      ut.run_prodigy_db_out("tom_stiching", "", "tom_output_stiching.jsonl")
      stiching_docs = [json.loads(line) for line in open("tom_output_stiching.jsonl")]
      correct_docs = [json.loads(line) for line in open("no_need_to_correct.jsonl")]
      total_doc = stiching_docs + correct_docs
      output_stiching_complete = open("tom_complete_after_stiching.jsonl")

      for doc in total_doc:
        json.dump(doc, output_stiching_complete)
        
      # output_file = open("tom_output_total.jsonl", "w")
      # for item in total_doc:
      #     json.dump(item, output_file)
      #     output_file.write("\n")


      total_doc = ut.read_data_base("tom_output_total.jsonl", annotator_name="tom")
      correction_tsv_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "tsvs" / 'corrections_tom.tsv'
      ut.visualize_the_annotations_to_tsv(total_doc, correction_tsv_file)
      
      test_keys, dev_keys = dc.get_test_indexes(correction_tsv_file)
      # dc.create_annotated_covid(True, args.root, correction_tsv_file, test_keys, dev_keys, args.output_data_name)
      # print('mech only data created')
      # dc.create_annotated_covid(False, args.root, correction_tsv_file, test_keys, dev_keys, args.output_data_name)
      # print('mech effect data created')
      # dc.write_gold_file(True, args.root, correction_tsv_file, test_keys, args.output_data_name)
      # print('mech only gold created')

      # dc.write_gold_file(False, args.root, correction_tsv_file, test_keys, args.output_data_name)
      # print('mech effect gold created')
      dc.write_gold_file(False, args.root, correction_tsv_file, dev_keys, "dev_" + args.output_data_name)
      dc.write_gold_file(True, args.root, correction_tsv_file, dev_keys, "dev_" + args.output_data_name)

  elif args.command_type == "sort_data_for_stats":
    #getting all the files that arae needed for the agreement stats
    #first step getting all initia annotations
    ut.update_extractions(ut.DEFAULT_NAME_LIST, ut.ANNOTATION_DIR_PATH, annotations_correction="annotations")
    ut.update_extractions(ut.DEFAULT_CORRECTION_NAME_LIST, ut.SELF_CORRECTION_DIR_PATH, annotations_correction="correction")
    ut.merge_with_old(ut.ANNOTATION_DIR_PATH + "jsons/", ut.ANNOTATION_DIR_PATH_OLD + 'jsons/')
    ut.merge_with_old(ut.SELF_CORRECTION_DIR_PATH + "jsons/", ut.CORRECTION_DIR_PATH_OLD + 'jsons/')
    for name in ut.DEFAULT_NAME_LIST:
        annotation_name = 'annotations_' + name + '.jsonl'
        annotation_name_tsv = 'annotations_' + name + '.tsv'
        annotation_json_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "jsons" / annotation_name
        annotation_tsv_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "tsvs" / annotation_name_tsv
        data_list =  ut.read_data_base(str(annotation_json_file), name)
        ut.visualize_the_annotations_to_tsv(data_list, annotation_tsv_file)
    for name in ut.DEFAULT_CORRECTION_NAME_LIST:
        annotation_name = 'corrections_' + name + '.jsonl'
        annotation_name_tsv = 'corrections_' + name + '.tsv'
        correction_json_file = pathlib.Path(ut.SELF_CORRECTION_DIR_PATH) / "jsons" / annotation_name
        correction_tsv_file = pathlib.Path(ut.SELF_CORRECTION_DIR_PATH) / "tsvs" / annotation_name_tsv
        data_list =  ut.read_data_base(str(correction_json_file), name)
        ut.visualize_the_annotations_to_tsv(data_list, correction_tsv_file)

    # #get toms annotations that madeline corrected. 
    # ut.run_prodigy_db_out("ner_rels_bio_madeline_correction", 'validations/', "madeline_tom.jsonl")
    # data_list =  ut.read_data_base("validations/"  + "madeline_tom.jsonl", "tom")
    # ut.visualize_the_annotations_to_tsv_reverse(data_list, "validations/madeline_tom.tsv")
    # data_list =  ut.read_data_base(""  + "validation_input_madeline.jsonl", "tom")

    # ut.visualize_the_annotations_to_tsv(data_list, "validations/input_madeline_tom.tsv")
  elif args.command_type == "madeline_final":
    ut.run_prodigy_db_out("ner_rels_bio_madeline_correction","validations/", "madeline_final.jsonl")
    
    #fix stichings 
    doc_id_list = ks.find_the_ids_with_issues("validations/madeline_final.jsonl")
    ks.write_stiching_docs("metadata", "validations/madeline_final.jsonl", doc_id_list, "validations/for_madeline_final_stiching.jsonl","validations/madeline_final_corrected.jsonl")


    data_list =  ut.read_data_base("validations/madeline_final_corrected.jsonl", "madeline")
    print(len(data_list))
    ut.visualize_the_annotations_to_tsv_reverse(data_list, "validations/madeline_final.tsv")



    test_keys, dev_keys = dc.get_test_indexes("validations/madeline_final.tsv")
    dc.create_annotated_covid(True, args.root, "validations/madeline_final.tsv", test_keys, dev_keys, "madeline_final")
    print('mech only data created')
    dc.create_annotated_covid(False, args.root, "validations/madeline_final.tsv", test_keys, dev_keys, "madeline_final")
    print('mech effect data created')
    dc.write_gold_file(True, args.root, "validations/madeline_final.tsv", test_keys, "madeline_final")
    print('mech only gold created')

    dc.write_gold_file(False, args.root, "validations/madeline_final.tsv", test_keys, "madeline_final")
    print('mech effect gold created')
    dc.write_gold_file(False, args.root, "validations/madeline_final.tsv", dev_keys, "dev_" + "madeline_final")
    dc.write_gold_file(True, args.root, "validations/madeline_final.tsv", dev_keys, "dev_" + "madeline_final")


  elif args.command_type == "madeline_final_and_stiching":
    ut.run_prodigy_db_out("ner_rels_bio_madeline_correction","validations/", "madeline_final.jsonl")
    
    #fix stichings 
    doc_id_list = ks.find_the_ids_with_issues("validations/madeline_final.jsonl")
    ks.write_stiching_docs("metadata", "validations/madeline_final.jsonl", doc_id_list, "validations/for_madeline_final_stiching.jsonl","validations/madeline_final_corrected.jsonl")
    #at the moment we are reading tom's annotations for stichings

    ut.run_prodigy_db_out("tom_stiching", "", "tom_output_stiching.jsonl")
    stiching_docs = ut.read_data_base("tom_output_stiching.jsonl", "tom")

    data_list =  ut.read_data_base("validations/"  + "madeline_final_corrected.jsonl", "madeline")
    data_list = data_list + stiching_docs
    print(len(data_list))
    ut.visualize_the_annotations_to_tsv_reverse(data_list, "validations/madeline_final_stichings.tsv")



    test_keys, dev_keys = dc.get_test_indexes("validations/madeline_final_stichings.tsv")
    dc.create_annotated_covid(True, args.root, "validations/madeline_final_stichings.tsv", test_keys, dev_keys, "madeline_final_stichings")
    print('mech only data created')
    dc.create_annotated_covid(False, args.root, "validations/madeline_final_stichings.tsv", test_keys, dev_keys, "madeline_final_stichings")
    print('mech effect data created')
    dc.write_gold_file(True, args.root, "validations/madeline_final_stichings.tsv", test_keys, "madeline_final_stichings")
    print('mech only gold created')

    dc.write_gold_file(False, args.root, "validations/madeline_final_stichings.tsv", test_keys, "madeline_final_stichings")
    print('mech effect gold created')
    dc.write_gold_file(False, args.root, "validations/madeline_final_stichings.tsv", dev_keys, "dev_" + "madeline_final_stichings")
    dc.write_gold_file(True, args.root, "validations/madeline_final_stichings.tsv", dev_keys, "dev_" + "madeline_final_stichings")
