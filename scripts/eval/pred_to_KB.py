import networkx as nx

wordnet_lemmatizer = WordNetLemmatizer()

spacy_nlp = spacy.load('en_core_web_sm')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
# nlp = spacy.load("en_core_sci_sm")
G = nx.MultiDiGraph()  # to keep the sentences helped matching and all versions 

CUDA_DEVICE = 1
DATA_PREFIX = "/data/aida/cord19_sentences/partitions_small/"
MODEL_PATH = "/data/aida/covid_aaai/experiments/covid_anno_par_madeline_sentences_matchcd/mapped/mech_effect/run_14_2020-08-31_12-41-475u0tjm18/trial/"
PRED_DIR = "/data/aida/covid_aaai/predictions_small/KB"



def read_merge_predictions():
  relation_seen_count = {}
  span_seen_count = {}
  errors_filepath = open("not_complete.txt", "w")
  file_names = glob(PRED_DIR+"/*.jsonl")
  count = 0
  for name in file_names:
    if count == 100:
      break
    count += 1
    print(name)
    pred_data = [json.loads(line) for line in open(name)]
    
    if len(pred_data) != 100:  # checking if we get the complete predictions for file
      errors_filepath.write(name)

    ds = Dataset(name)
    pred_rels = get_doc_key_info(ds)
    for item in pred_rels:
      arg0_rep = get_representation_string(item[2])
      arg1_rep = get_representation_string(item[3])

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
  import pdb; pdb.set_trace()
  for item in  span_seen_count:
      output_file_spans.write(item + '\t' + str(span_seen_count[item]) + '\n')
  for item in  relation_seen_count:
      output_file_rels.write(str(item) + '\t' + str(relation_seen_count[item]) + '\n')
