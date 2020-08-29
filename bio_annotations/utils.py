import pathlib
import subprocess
import json
from pathlib import Path
from os import listdir
from os.path import isfile, join

import spacy

NLP = spacy.load("en_core_web_sm")
PRODIGY_FILE = "prodigy.json"
SELF_CORRECTION_DIR_PATH = "self_corrections/"
CORRECTION_DIR_PATH = "corrections/"
ANNOTATION_DIR_PATH = "annotations/"
ANNOTATION_DIR_PATH_OLD = "annotations_old/"
CORRECTION_DIR_PATH_OLD = "corrections_old/"

DEFAULT_NAME_LIST = ["madeline", "megan", "sara", "yeal", "tom", "kristina", "jeff"]
DEFAULT_CORRECTION_NAME_LIST = ["madeline", "megan", "sara"]

def find_span_start_token_in_text(text, span):
    text_tokens = process_paragraph(text)
    span_tokens = process_paragraph(span)
    start_index = -1
    span_found = False
    while start_index < len(text_tokens):
      if text_tokens[start_index] == span_tokens[0]:
        span_found = True
        for i in range(len(span_tokens)):
          if start_index + i < len(text_tokens) or span_tokens[i] != text_tokens[start_index + i]:
            span_found = False
            break
      if span_found == True:
        return start_index
      start_index += 1
    return -1


def find_stats_span_distance(dataset):
    # the data set it a list of data
    #each data point is a list of [id, text, arg0, arg1]
    ave_distance = 0
    total_count = 0
    max_distance = 0
    for data in dataset:
      arg0_index = find_span_start_token_in_text(data[1], data[2])
      arg1_index = find_span_start_token_in_text(data[1], data[3])
      total_count += 1
      dist = abs(arg1_index - arg0_index)
      ave_distance += dist
      if dist > max_distance:
        max_distance = dist
    print("average distance of spans is : " + str(float(ave_distance)/total_count))
    print("max distance of spans in a relation  is : " + str(max_distance))

def find_stats_span_length(dataset):
    # the data set it a list of data
    #each data point is a list of [id, text, arg0, arg1]
    total_count = 0
    arg0_ave = 0
    arg1_ave = 0
    for data in dataset:
      args0_toks = process_paragraph(data[2]) 
      args1_toks = process_paragraph(data[3])
      total_count += 1
      arg0_ave += len(args0_toks)
      arg1_ave += len(args1_toks)
    print("average length of spans in arg0 is :" + str(float(arg0_ave/total_count)))
    print("average length of spans in arg1 is :" + str(float(arg1_ave/total_count)))

def length_distributions(dataset):
    # the data set it a list of data
    #each data point is a list of [id, text, arg0, arg1] 
    arg0_len = [0 for x in range(40)]
    arg1_len = [0 for x in range(40)]
    for data in dataset:
      args0_toks = process_paragraph(data[2]) 
      args1_toks = process_paragraph(data[3])
      arg0_len[len(args0_toks)] += 1
      arg1_len[len(args1_toks)] += 1
    total_len = [arg0_len[x] + arg1_len[x] for x in range(len(arg0_len))]
    print("length distribution of spans in arg0 is :" + str(arg0_len))
    print("length distribution of spans in arg1 is :" + str(arg1_len))
    print("length distribution of spans in total args is :" + str(total_len))
    arg0_percentile = [sum(arg0_len[:i+1])/sum(arg0_len) for i in range(len(arg0_len)-1)]
    arg1_percentile = [sum(arg1_len[:i+1])/sum(arg1_len) for i in range(len(arg1_len)-1)]
    total_percentile = [sum(total_len[:i+1])/sum(total_len) for i in range(len(total_len)-1)]
    print("length percentiles of spans in arg0 is :" + str(arg0_percentile))
    print("length percentiles of spans in arg1 is :" + str(arg1_percentile))
    print("length percentiles of spans in total is :" + str(total_percentile))
    


def read_already_annotated(db_name_list):
    #used in functions to create unique new annotations. 
    # given the name of the dataset we get the list of what has been already save as annotated there
    key_pair_list = []
    for db_name in db_name_list:
      run_prodigy_db_out(db_name, "temp/", db_name + '.jsonl')
      db_file = open('temp/' + db_name + '.jsonl')
      for line in db_file:
          data = json.loads(line)
          doc_key = data['meta']['doc_key']
          text = data['text']
          if (doc_key, text) not in key_pair_list:
            key_pair_list.append((doc_key, text))
      return key_pair_list


def process_paragraph(paragraph):
    res = []
    text = NLP(paragraph)
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        all_tokens = all_tokens + tokens
    return all_tokens


def process_abstract(abstract, paper_id):
    sents = process_paragraph(abstract[0]['text'])
    return dict(doc_key=f"{paper_id}:abstract",
                section="Abstract",
                sentences=sents)


def convert_to_json(text, relation_pairs, doc_key):
  #converting from tsv to json in a format that prodigy can load into its scheme 
  res = {}
  res["text"] = text
  res["meta"] = {}
  res["meta"]["section"] = "Abstract"
  res["meta"]["doc_key"] = doc_key
  
  tokens = process_paragraph(text.replace("  ", " "))
  res["tokens"] = []
  res["spans"] = []
  res["relations"] = []

  seen_tokens = []
  ind_start = 0

  for i in range(len(tokens)):
    tok = tokens[i]
    tok_info = {}
    tok_info["text"] = tok
    try:
      tok_info["start"] = text.lower().index(tok.lower(), ind_start)
    except:
      import pdb; pdb.set_trace()
    tok_info["end"] = text.lower().index(tok.lower(), ind_start) + len(tok)
    
    # if tok not in seen_tokens:
    #   seen_tokens.append(tok)
    tok_info["id"] = i
    tok_info["disabled"] = False
    res["tokens"].append(tok_info)
    ind_start += len(tok)
    if ind_start < len(text) and text[ind_start] == " ":
      ind_start += 1
  res["_view_id"] = "relations"
  

  for info in relation_pairs:
    
    head_token_info = {}
    head_token_info["label"] = "ENTITY"
    # import pdb; pdb.set_trace()
    try:
      head_token_info["start"] = text.lower().index(info[1].strip().lower()+" ")
      head_token_info["end"] = text.lower().index(info[1].strip().lower()+" ") + len(info[1].strip().lower())
    except:
      if info[1].strip().lower() not in text.lower():
        import pdb; pdb.set_trace()
      head_token_info["start"] = text.lower().index(info[1].strip().lower())
      head_token_info["end"] = text.lower().index(info[1].strip().lower()) + len(info[1].strip().lower())

    child_token_info = {}
    child_token_info["label"] = "ENTITY"
    try:
      child_token_info["start"] = text.lower().index(info[2].strip().lower()+" ")
      child_token_info["end"] = text.lower().index(info[2].strip().lower()+" ") + len(info[2].strip().lower())
    except:
      if info[2].strip().lower() not in text.lower():
        import pdb; pdb.set_trace()
      child_token_info["start"] = text.lower().index(info[2].strip().lower())
      child_token_info["end"] = text.lower().index(info[2].strip().lower()) + len(info[2].strip().lower())

    for i in range(len(res["tokens"])):
      tok_inf = res["tokens"][i]
      
      if tok_inf["start"] == head_token_info["start"]:
        head_token_info["token_start"] = i
      if tok_inf["end"] == head_token_info["end"]:
        head_token_info["token_end"] = i - 1 
        if 'token_start' in head_token_info and head_token_info["token_end"] < head_token_info["token_start"]:
          head_token_info["token_end"] = head_token_info["token_start"]

      if tok_inf["start"] == child_token_info["start"]:
        child_token_info["token_start"] = i 
      if tok_inf["end"] == child_token_info["end"]:
        child_token_info["token_end"] = i - 1
        if 'token_start' in child_token_info and child_token_info["token_end"] < child_token_info["token_start"]:
          child_token_info["token_end"] = child_token_info["token_start"]
    
    res["spans"].append(head_token_info)
    res["spans"].append(child_token_info)

    relations_info = {}
    relations_info["label"] = info[0]
    relations_info["color"] = "#c5bdf4"
    relations_info["head_span"] = head_token_info
    relations_info["child_span"] = child_token_info
    if "token_end" not in head_token_info or "token_end" not in child_token_info:
      return {}
      import pdb; pdb.set_trace()
    relations_info["head"] = head_token_info["token_end"]
    relations_info["child"] = child_token_info["token_end"]

    res["relations"].append(relations_info)
  return res



def visualize_the_annotations_to_tsv(data_list, output_tsv_file_name):
    doc_key_list = []
    doc_key_sent_list = []
    output_tsv_file = open(output_tsv_file_name, 'w')
    # output_tsv_file.write("doc_key\ttext\thead\tchild\tlabel\t\taccept_reject\n")
    pruned_data = []
    for data in data_list:
        doc_key = data['meta']['doc_key']
        answer = data['answer']
        text = data['text']
        annotator_name = data["annotator"]
        if answer == "reject":
            # output_tsv_file.write(doc_key + '\t' + text + '\t\t\t\treject\n')
            continue
        elif answer == "ignore":
          continue
        if doc_key not in doc_key_list:
          doc_key_list.append(doc_key)
        if (doc_key, text) in doc_key_sent_list:
          continue
        doc_key_sent_list.append((doc_key, text))
        pruned_data.append(data)
        for i in range(len(data['relations'])):
          relations_head = text[data['relations'][i]['head_span']['start']:data['relations'][i]['head_span']['end']]
          if len(text)-1 > data['relations'][i]['head_span']["end"] and (text[data['relations'][i]['head_span']["end"]]) != " ":
              end_index = text.index(" ", data['relations'][i]['head_span']['end'])
              relations_head = text[data['relations'][i]['head_span']['start']:end_index]
              if relations_head[len(relations_head)-1] == '.' or relations_head[len(relations_head)-1] == '?' or relations_head[len(relations_head)-1] == '!':
                relations_head = relations_head[:-1]

          relations_child = text[data['relations'][i]['child_span']['start']:data['relations'][i]['child_span']['end']]
          if len(text)-1 > data['relations'][i]['child_span']["end"] and (text[data['relations'][i]['child_span']["end"]]) != " ":
              
              try:
                end_index = text.index(" ", data['relations'][i]['child_span']['end'])
              except:
                import pdb; pdb.set_trace()
              relations_child = text[data['relations'][i]['child_span']['start']:end_index]
              if relations_child[len(relations_child)-1] == '.' or relations_child[len(relations_child)-1] == '?' or relations_child[len(relations_child)-1] == '!':
                relations_child = relations_child[:-1]

          relation_label = data['relations'][i]['label']
          output_tsv_file.write(doc_key + '\t' + text.replace("  ", " ") + '\t' + relations_head.replace("  ", " ")+ '\t' + relations_child.replace("  ", " ") + '\t' + relation_label + '\taccept\t' + annotator_name + '\n')
    return pruned_data




def visualize_the_annotations_to_tsv_reverse(data_list, output_tsv_file_name):
    doc_key_list = []
    doc_key_sent_list = []
    output_tsv_file = open(output_tsv_file_name, 'w')
    # output_tsv_file.write("doc_key\ttext\thead\tchild\tlabel\t\taccept_reject\n")
    pruned_data = []
    for j in range(len(data_list)-1, -1, -1):
        data = data_list[j]
        doc_key = data['meta']['doc_key']
        answer = data['answer']
        text = data['text']
        annotator_name = data["annotator"]
        if answer == "reject":
            # output_tsv_file.write(doc_key + '\t' + text + '\t\t\t\t\treject\n')
            continue
        elif answer == "ignore":
          # output_tsv_file.write(doc_key + '\t' + text + '\t\t\t\t\tignore\n')
          continue
        if doc_key not in doc_key_list:
          doc_key_list.append(doc_key)
        if (doc_key, text) in doc_key_sent_list:
          continue
        doc_key_sent_list.append((doc_key, text))
        pruned_data.append(data)
        for i in range(len(data['relations'])):
          relations_head = text[data['relations'][i]['head_span']['start']:data['relations'][i]['head_span']['end']]
          if len(text)-1 > data['relations'][i]['head_span']["end"] and (text[data['relations'][i]['head_span']["end"]]) != " ":
              end_index = text.index(" ", data['relations'][i]['head_span']['end'])
              relations_head = text[data['relations'][i]['head_span']['start']:end_index]
              if relations_head[len(relations_head)-1] == '.' or relations_head[len(relations_head)-1] == '?' or relations_head[len(relations_head)-1] == '!':
                relations_head = relations_head[:-1]

          relations_child = text[data['relations'][i]['child_span']['start']:data['relations'][i]['child_span']['end']]
          if len(text)-1 > data['relations'][i]['child_span']["end"] and (text[data['relations'][i]['child_span']["end"]]) != " ":
              
              try:
                end_index = text.index(" ", data['relations'][i]['child_span']['end'])
              except:
                import pdb; pdb.set_trace()
              relations_child = text[data['relations'][i]['child_span']['start']:end_index]
              if relations_child[len(relations_child)-1] == '.' or relations_child[len(relations_child)-1] == '?' or relations_child[len(relations_child)-1] == '!':
                relations_child = relations_child[:-1]

          relation_label = data['relations'][i]['label']
          output_tsv_file.write(doc_key + '\t' + text.replace("  ", " ") + '\t' + relations_head.replace("  ", " ")+ '\t' + relations_child.replace("  ", " ") + '\t' + relation_label + '\taccept\t' + annotator_name + '\n')
    return pruned_data

def run_prodigy_command(data_file_name, dataset_name, port_num, label_list=["DO", "USED", "EFFECT"], entity_list=["ENTITY"]):
    write_prodigy_port(port_num)
    prodigy_command = [
      'prodigy',
      'rel.manual',
      dataset_name,
      'blank:en',
      data_file_name,
      "--label",
      ','.join(label_list),
      "--span-label",
      ','.join(entity_list)
    ]
    subprocess.run(" ".join(prodigy_command), shell=True, check=True)


def run_prodigy_db_out(db_name, output_dir, output_file_name):
    prodigy_command = [
      'prodigy',
      'db_out',
      db_name,
      '>' + output_dir + output_file_name
    ]
    subprocess.run(" ".join(prodigy_command), shell=True, check=True)

def read_data_base(database_filename, annotator_name=""):
  data_list = [] 
  db_file = open(database_filename)
  for line in db_file:
      data = json.loads(line)
      data['annotator'] = annotator_name
      data_list.append(data)
  return data_list

def write_prodigy_port(port_num):
    input_file = open(PRODIGY_FILE)
    data = json.load(input_file)
    data['port'] = port_num
    output_file = open(PRODIGY_FILE, "w")
    json.dump(data, output_file, indent=4)

def update_extractions(name_list, annotation_path, annotations_correction="annotations",dataset_suffix="_correction"):
  for name in name_list:
    if name =="jeff" or name== "kristina":
      continue
    db_file = "ner_rels_bio_" + name
    # if name == "sara":
    #   db_file = "ner_rels_bio_sara_v2"    
    annotation_name = 'annotations_' + name + '.jsonl'
    annotation_output_file = pathlib.Path(annotation_path) / "jsons" 

    if annotations_correction == "correction":
      annotation_name = 'corrections_' + name + '.jsonl'
      annotation_output_file = pathlib.Path(annotation_path) / "jsons" 
      db_file = db_file + dataset_suffix
      if name == "tom":
        db_file = db_file + "_NEW"
    run_prodigy_db_out(db_file, str(annotation_output_file) + '/' , annotation_name)
    print("retrieved annotations of " + name)

def merge_with_old(new_path, old_path):
    #my function so that we can merge with what we had before once clearing the cache
    new_files = [f for f in listdir(new_path) if (isfile(join(new_path, f)) and f.endswith('jsonl'))]
    old_files = [f for f in listdir(old_path) if (isfile(join(old_path, f)) and f.endswith('jsonl'))]
    for file in old_files:
      if file in new_files:
        new_docs = [json.loads(line) for line in open(join(new_path, file))]
        old_docs = [json.loads(line) for line in open(join(old_path, file))]
        total_docs = new_docs + old_docs

        
      else:
        total_docs = [json.loads(line) for line in open(join(old_path, file))]

      output_file = open(join(new_path, file), "w")
      for line in total_docs:
        json.dump(line, output_file)
        output_file.write("\n")






