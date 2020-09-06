import os
import json
import multiprocessing
import re
import nltk
from nltk.stem import WordNetLemmatizer
from glob import glob 
import spacy
from dygie_visualize_util import Dataset
import networkx as nx

wordnet_lemmatizer = WordNetLemmatizer()

spacy_nlp = spacy.load('en_core_web_sm')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
# nlp = spacy.load("en_core_sci_sm")
Global_graph = nx.MultiDiGraph()  # to keep the sentences helped matching and all versions 
node_list = {}

CUDA_DEVICE = 1
DATA_PREFIX = "/data/aida/cord19_sentences/partitions_small/"
MODEL_PATH = "/data/aida/covid_aaai/experiments/covid_anno_par_madeline_sentences_matchcd/mapped/mech_effect/run_14_2020-08-31_12-41-475u0tjm18/trial/"
PRED_DIR = "/data/aida/covid_aaai/predictions_small/KB"

class Node:
  def __init__(self,representation, text):
    self.representation = representation
    self.text_seen_list = []
    self.text_seen_list.append(text)

class Edge:
  def __init__(self,node0, node1, original_text0, original_text1, sent):
    self.sent = sent
    self.node0 = node0
    self.node1 = node1
    self.original_text0 = original_text0
    self.original_text1 = original_text1


def get_doc_key_info(ds):
  doc_info_conf_iter = {}
  for doc in ds:
    doc_key = doc._doc_key
    for sent in doc:
      sent_text = " ".join(sent.text)
      for rel in sent.relations:
        arg0 = " ".join(rel.pair[0].text)
        arg1 = " ".join(rel.pair[1].text)
        data_key = (doc_key, sent_text, arg0, arg1, rel.label)
        doc_info_conf_iter[data_key] = rel.score
  return doc_info_conf_iter


def create_eval_command_partition(cuda_device, index_num):
    return  "allennlp predict " + MODEL_PATH + " " + \
      DATA_PREFIX + "/covid19_" + str(index_num) + ".jsonl"  + \
      " --predictor dygie " + \
      " --include-package dygie " + \
      " --use-dataset-reader " + \
      " --output-file " + PRED_DIR + "/covid19_" +str(index_num)+ ".jsonl " +  \
      "--cuda-device 1"
 
def merge_eval_partitions(iterations_num):
  file_list = ["predictions/predictions_Dygie_iter" + str(iterations_num) + "_partition_" +str(index_num)+ ".jsonl " for index_num in range(0,48)]
  output_file = "predictions/predictions_Dygie_iter" + str(iterations_num) + ".jsonl"
  for file in file_list:
    inp_file = open(file)
    for line in inp_file:
      output_file.write(line)


def filter_stopwords(tokens):
    return " ".join([t for t in tokens if t.lower() not in spacy_stopwords])


def eval_safe_process(eval_command_line):
    try:
        os.system(eval_command_line)
    except Exception as e:
        print(f"{eval_command_line}: error")



def parition_eval_procedure():
    workers = multiprocessing.Pool(2)
    eval_command_line_list = [create_eval_command_partition(CUDA_DEVICE, i) for i in range(0, 500)]
    workers.map(eval_safe_process, eval_command_line_list)
    

def get_representation_string(word):
  word = re.sub(r'[^\w\s]','',word).lower()  # removing all the punctuations.
  word = re.sub(r'  ',' ',word)  # removing all the punctuations.
  word = filter_stopwords(word.split())  # remoding stop words
  word = " ".join([wordnet_lemmatizer.lemmatize(part) for part in word.split()])  # getting lemma of each word 
  return word

def process_edge(item, arg0_rep, arg1_rep, weight):
  node0 = Node(arg0_rep, item[2])
  node1 = Node(arg1_rep, item[3])
  Global_graph.add_node(node0)
  Global_graph.add_node(node1)
  Global_graph.add_edge(node0, node1, weight, label=item[1], doc_id=item[0])
  import pdb; pdb.set_trace()

def check_contains_refrence(word):
  refrence_words = ["they", "it", "these", "those", "that", "this"]
  word_parts = word.split()
  for part in word_parts:
    if part in refrence_words:
      return True
  return False


def read_coref_file(coref_file_path):
  res = {}
  input_file = open(coref_file_path)
  for line in input_file:
    contains_refrence = False
    line_parts = line[:-1].split("\t")
    doc_id = line_parts[0]
    if doc_id not in res:
      res[doc_id ] = []
    new_row = []
    new_row.append({"text": line_parts[2]})
    if check_contains_refrence(line_parts[2]):
        contains_refrence = True

    for i in range(3, len(line_parts)):
      new_coref = {}
      item_parts = line_parts[i].split("|")
      if check_contains_refrence(item_parts[0]):
        contains_refrence = True
      new_coref = {"text": item_parts[0], "start": item_parts[1], "end": item_parts[2]}
      new_row.append(new_coref)
    if contains_refrence:
      res[doc_id].append(new_row)
  return res

def replace_coref_span(span, text, doc_coref_data):
  for coref_doc in doc_coref_data:
    for i in range(1, len(coref_doc)):
      # import pdb; pdb.set_trace()
      if coref_doc[i]["text"] in span and check_contains_refrence(coref_doc[i]["text"]) == True:
        print(span + "\t" + coref_doc[i]["text"] + "\t" + coref_doc[0]["text"])
        return span.replace(coref_doc[i]["text"], coref_doc[0]["text"])
  return span

def replace_coref(input_filepath, output_filepath, coref_path):
  coref_data = read_coref_file(coref_path)
  print(len(coref_data))
  input_file = open(input_filepath)
  output_file = open(output_filepath, "w")
  for line in input_file:

    line_parts = line[:-1].split("\t")
    # import pdb; pdb.set_trace()
    # if line_parts[0] in coref_data:
    #   print( line_parts[0] in coref_data)
    if check_contains_refrence(line_parts[2]) == False and check_contains_refrence(line_parts[3]) == False or line_parts[0] not in coref_data:
      output_file.write(line)
      continue
    if check_contains_refrence(line_parts[2]) == True:
      doc_coref_data = coref_data[line_parts[0]]
      line_parts[2] = replace_coref_span(line_parts[2], line_parts[1], doc_coref_data)

    if check_contains_refrence(line_parts[3]) == True:
      doc_coref_data = coref_data[line_parts[0]]
      line_parts[3] = replace_coref_span(line_parts[3], line_parts[1], doc_coref_data)

    arg0_rep = get_representation_string(line_parts[2])
    arg1_rep = get_representation_string(line_parts[3])
    output_file.write("\t".join(line_parts[:4]) +'\t' + arg0_rep + '\t' + arg1_rep+ '\t' + line_parts[7]+ '\n')


def read_merge_predictions():
  relation_seen_count = {}
  span_seen_count = {}
  errors_filepath = open("not_complete.txt", "w")
  output_file = open("complete_KB.tsv", "w")
  output_file.write("doc_id\tsentence\tspan1\tspan2\trelation_tag\tspan1_lemma\tspan2_lemma\tconf\n")
  file_names = glob(PRED_DIR+"/*.jsonl")
  count = 0
  for name in file_names:
    print(name)
    pred_data = [json.loads(line) for line in open(name)]
    
    if len(pred_data) != 100:  # checking if we get the complete predictions for file
      errors_filepath.write(name)

    ds = Dataset(name)
    pred_rels = get_doc_key_info(ds)
    for item in pred_rels:
      arg0_rep = get_representation_string(item[2])
      arg1_rep = get_representation_string(item[3])
      # import pdb; pdb.set_trace()
      # process_edge(item, arg0_rep, arg1_rep, pred_rels[item])
      output_file.write(item[0] + '\t' + item[1] + '\t' + item[2] + '\t' + item[3] + '\t' + item[4] + '\t' + arg0_rep + '\t' + arg1_rep + '\t' + str(pred_rels[item]) + '\n')
      if arg0_rep not in span_seen_count:
        span_seen_count[arg0_rep] = 1
      else:
        span_seen_count[arg0_rep] += 1

      if arg1_rep not in span_seen_count:
        span_seen_count[arg1_rep] = 1
      else:
        span_seen_count[arg1_rep] += 1

      if (arg0_rep, arg1_rep) not in relation_seen_count:
        relation_seen_count[(arg0_rep, arg1_rep)] = 1
      else:
        relation_seen_count[(arg0_rep, arg1_rep)] += 1


  output_file_spans = open("kb_spans.txt", "w")
  output_file_rels = open("kb_rels.txt", "w")
  # import pdb; pdb.set_trace()
  for item in  span_seen_count:
      output_file_spans.write(item + '\t' + str(span_seen_count[item]) + '\n')
  for item in  relation_seen_count:
      output_file_rels.write(str(item) + '\t' + str(relation_seen_count[item]) + '\n')

if __name__ == "__main__":
  # parition_eval_procedure()
    replace_coref("complete_KB.tsv", "complete_KB_coref.tsv", "/data/dave/proj/for-aida/coref-predictions-2020-09-04/unlabeled/merged.tsv")
    # read_merge_predictions()














