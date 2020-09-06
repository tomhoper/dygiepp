import json
import eval_utils as eu
import pathlib
from pathlib import Path
import pandas as pd
import itertools


PREDICTION_DIR = "validation_ranks/"
PREDICTION_STATS = "pred_stats/"

def calc_accept_rate_per_alg(data_list):
  method_sample_count = {}
  method_accept_count = {}
  for item in data_list:
      method_name = item["meta"]["doc_key"].split("__")[1]
      if method_name not in method_sample_count:
        method_sample_count[method_name] = 1.0
        method_accept_count[method_name] = 0.0
      else:
        method_sample_count[method_name] += 1.0
      if item["answer"] == "accept":
        method_accept_count[method_name] += 1.0

  for item in method_sample_count:
      print(item + "    " + str(method_sample_count[item]))
      print("accept rate for item: " + item + "   " + str(method_accept_count[item]/method_sample_count[item])) 

def find_max_score(combo, metirc, consider_reverse, collapse):
    final_score = 0
    for pair in combo:
      if pair[1][0] == "A sound clinician understanding of anatomic neck spaces and common etiologies of pediatric neck masses":
        import pdb; pdb.set_trace()
      try:
        if len(pair[1][1]) == 1 or len(pair[0][0]) == 1:
          import pdb; pdb.set_trace()
      except:
          import pdb; pdb.set_trace()

      span0_score = eu.span_score(pair[0][0], pair[1][0],metric=metirc)
      span1_score = eu.span_score(pair[0][1], pair[1][1],metric=metirc)

      if collapse:
        total_score = min(span0_score, span1_score)
      else:
        if pair[0][2]==pair[1][2]:
          total_score = min(span0_score, span1_score)
        else:
          total_score = 0 
      if consider_reverse == True:
        span0_score = eu.span_score(pair[0][0], pair[1][1],metric=metirc)
        span1_score = eu.span_score(pair[0][1], pair[1][0],metric=metirc)
        if collapse:
          reverse_score = min(span0_score, span1_score)
        else:
          if pair[0][2]==pair[1][2]:
            reverse_score = min(span0_score, span1_score)
          else:
            reverse_score = 0 
        total_score = max(total_score, reverse_score)

      final_score = max(final_score, total_score)
    return final_score

def write_tsv_for_scores_per_alg(predf, golddf, output_file_name):
    goldrels = golddf[["id","arg0","arg1","rel", "text"]]#.drop_duplicates()
    goldrels = goldrels.drop_duplicates(subset =["id","arg0","arg1","text"]).set_index(["id"])
    # predrels = predf[["id","arg0","arg1","rel"]].set_index(["id"],inplace=False)
    output_file = open(output_file_name, "w")
    
    output_file.write("id\t" + "method\t" + "arg0\t" + 'arg1\t' + "answer")
    for metric in ["substring", "jaccard", "rouge"]:
        for consider_reverse in [True, False]:
          for collapse in [True, False]:   
            header = metric + "_reverse:" + str(consider_reverse) + "_collapse:" + str(collapse)
            output_file.write('\t' + header)
    output_file.write("\n")

    
    for rel in predf.iterrows():
      i = rel[1]["id"]
      method_name = rel[1]["method"]
      arg0 = rel[1]["arg0"]
      arg1 = rel[1]["arg1"]
      answer = rel[1]["answer"]
      output_file.write(i + '\t' + method_name + '\t' + arg0 + '\t'+ arg1 + '\t' + answer)  
      # pred = predrels.loc[[(i, arg0, arg1)]].set_index(["id"])
      pred = rel[1].to_frame().T
      pred = pred[["id","arg0","arg1","rel"]]
      pred = pred.set_index(["id"],inplace=False)
      for metric in ["substring", "jaccard", "rouge"]:
        for consider_reverse in [True, False]:
          for collapse in [True, False]:   
              gold = goldrels.loc[[i]]
              # import pdb; pdb.set_trace()

              combo = list(itertools.product(gold.values, pred.values))
              score = find_max_score(combo, metric, consider_reverse, collapse)
              output_file.write('\t' + str(score))
              
      output_file.write('\n')

def calc_original_accept_per_alg(predf, golddf, metic, thresh=0.3, filter_stop=False, consider_reverse=False, collapse=False):
    goldrels = golddf[["id","arg0","arg1","rel"]]#.drop_duplicates()
    goldrels = goldrels.drop_duplicates(subset =["id","arg0","arg1"]).set_index(["id"])
    predrels = predf[["id","arg0","arg1","rel"]].set_index(["id"],inplace=False)
    matched_predictions = []
    # import pdb; pdb.set_trace()
    method_sample_count = {}
    accept_by_code_count = {}
    reject_by_code_count = {}
    method_true_accept = {}
    method_true_reject = {}
    method_false_accept = {}
    method_false_reject = {}

    for i in predrels.index.unique():
        if i in goldrels.index.unique():
            gold = goldrels.loc[[i]]
            if type(predrels.loc[i]) == pd.core.series.Series:
                preds = [predrels.loc[i].values]
            else:
                preds = predrels.loc[i].values
            combo = list(itertools.product(gold.values, preds))
            # import pdb; pdb.set_trace()
            for pair in combo:
                if collapse:
                    labels = [1,1]
                else:
                    labels = [pair[0][2],pair[1][2]]
                match = eu.relation_matching(pair,metric=metric, labels = labels, consider_reverse=consider_reverse)
                if match and [i,pair[0][0],pair[0][1]] not in matched_predictions:
                  # print(type(pair))
                  if len(pair[1][1]) == 1 or len(pair[0][0]) == 1:
                    import pdb; pdb.set_trace()
                  matched_predictions.append([i,pair[1][0],pair[1][1]])

    for rel in predf.iterrows():
      method_name = rel[1]["method"]
      doc_key = rel[1]["id"]
      arg0 = rel[1]["arg0"]
      arg1 = rel[1]["arg1"]
      answer = rel[1]["answer"]
      if method_name not in method_sample_count:
          method_sample_count[method_name] = 1.0
          method_true_reject[method_name] = 0.0
          method_true_accept[method_name] = 0.0
          method_false_reject[method_name] = 0.0
          method_false_accept[method_name] = 0.0
          accept_by_code_count[method_name] = 0.0
          reject_by_code_count[method_name] = 0.0
      else:
          method_sample_count[method_name] += 1.0
      
      if [doc_key, arg0, arg1] in matched_predictions:
        accept_by_code_count[method_name] += 1.0
      else:
        reject_by_code_count[method_name] += 1.0

      if [doc_key, arg0, arg1] in matched_predictions and answer == "accept":
        method_true_accept[method_name] += 1.0
      if [doc_key, arg0, arg1] in matched_predictions and answer != "accept":
        method_false_accept[method_name] += 1.0
      if [doc_key, arg0, arg1] not in matched_predictions and answer == "accept":
        method_false_reject[method_name] += 1.0
      if [doc_key, arg0, arg1] not in matched_predictions and answer != "accept":
        method_true_reject[method_name] += 1.0
  
    # print(matched_predictions)
    for method in method_sample_count:
      # import pdb; pdb.set_trace()
      # if method_name == "srl":
      #   import pdb; pdb.set_trace()
      print("for method: " + method)
      print("true accept is " + str(method_true_accept[method]/accept_by_code_count[method]))
      print("true reject is " + str(method_true_reject[method]/reject_by_code_count[method]))
      print("false accept is " + str(method_false_accept[method]/accept_by_code_count[method]))
      print("false reject is " + str(method_false_reject[method]/reject_by_code_count[method]))
    
def convert_to_tsv(input_filepath):
    output_file = open(input_filepath[:-6] + '.tsv', "w")
    docs = [json.loads(line) for line in open(input_filepath)]
    if "eval_sents_tom" in input_filepath:
      redo_docs = [json.loads(line) for line in open(PREDICTION_DIR + "eval_sents_tom_redo.jsonl")]
      docs = redo_docs + docs[100:]
    for item in docs:
        arg0 = item['text'][item['relations'][0]['head_span']['start']:item['relations'][0]['head_span']['end']]
        arg1 = item['text'][item['relations'][0]['child_span']['start']:item['relations'][0]['child_span']['end']]
        label = item['relations'][0]['label']
        output_file.write(item["meta"]["doc_key"].split("__")[0] + '\t' + item["meta"]["doc_key"].split("__")[1] + \
          "\t" + arg0 + '\t' + arg1 + '\t' + label + '\t' + item['answer'] + '\t' + item['text'] + '\n')

def write_from_score_tsv():
  score_file = open("human_annotations_sentences_scores.tsv")
  tsv_file_tom = open( PREDICTION_DIR + "eval_sents_tom" + '.tsv')
  tsv_file_madeline = open( PREDICTION_DIR + "eval_sents_madeline_redo" + '.tsv')
  output_file = open( PREDICTION_STATS + "eval_sents_final" + '.tsv', "w")
  output_file.write("id\t" + "method\t" + "arg0\t" + 'arg1\t' + "answer_tom\t" + "answer_madeline")
  for metric in ["rouge", "substring", "jaccard"]:
          header = metric + "_reverse:True"  + "_collapse:True" 
          output_file.write('\t' + header)
  output_file.write("\n")
  score_data = {}
  tom_data = {}
  madeline_data = {}
  first_line = True
  for line in score_file:
    if first_line:
      first_line = False
      continue
    score_line_parts = line[:-1].replace("\t ", "\t").lower().split("\t")
    data = score_line_parts[:5]
    # if "administrative actions" in line:
      # import pdb; pdb.set_trace()
    for i in range(5,8):
      # import pdb; pdb.set_trace()
      score_line_parts[i] = score_line_parts[i].replace("(", "").replace(")", "").split(", ")
      data.append(min(float(score_line_parts[i][0]),float(score_line_parts[i][1])))
    if (score_line_parts[3], score_line_parts[4]) not in score_data:
      score_data[(score_line_parts[3], score_line_parts[4])] = data
    else:
      prev_data = score_data[(score_line_parts[3], score_line_parts[4])]

      for i in range(5,8):

        if data[i] < prev_data[i]:
          data[i] = prev_data[i]
      
      score_data[(score_line_parts[3], score_line_parts[4])] = data


  for line in tsv_file_tom:
    score_line_parts = line[:-1].lower().split("\t")
    tom_data[(score_line_parts[2], score_line_parts[3])] = score_line_parts
  for line in tsv_file_madeline:
    score_line_parts = line[:-1].lower().split("\t")
    madeline_data[(score_line_parts[2], score_line_parts[3])] = score_line_parts
  
  for item in tom_data:
    # if "by extraneous factors and administrative actions" in item:
      # import pdb; pdb.set_trace()
    if item not in madeline_data:
      continue
    

    if item in score_data:
      scores = score_data[item][5:8]
    else:
      scores = [0 for x in range(3)]
    for i in range(3):
      scores[i] = str(scores[i])
    # import pdb; pdb.set_trace()
    output_file.write('\t'.join(tom_data[item][0:4]) + '\t' + tom_data[item][5] + '\t' +madeline_data[item][5] + '\t' + '\t'.join(scores) + '\n')




def read_data(input_filepath):
    docs = [json.loads(line) for line in open(input_filepath)]
    if "eval_sents_tom" in input_filepath:
      redo_docs = [json.loads(line) for line in open(PREDICTION_DIR + "eval_sents_tom_redo.jsonl")]
      docs = redo_docs + docs[101:]

    return docs

if __name__ == '__main__':
    convert_to_tsv(PREDICTION_DIR + "eval_sents_tom.jsonl")
    # convert_to_tsv(PREDICTION_DIR + "eval_parts_tom.jsonl")
    convert_to_tsv(PREDICTION_DIR + "eval_sents_madeline_redo.jsonl")
    # convert_to_tsv(PREDICTION_DIR + "eval_parts_madeline.jsonl")

    GOLD_SENT_PATH = pathlib.Path("/data/aida/covid_aaai/gold_madeline_sentences_matchcd/mech_effect/gold_par.tsv")
    GOLD_PART_PATH = pathlib.Path("/data/aida/covid_aaai/gold_madeline_final/mech_effect/gold_par.tsv")
    write_from_score_tsv()
    # for fil0in ["eval_sents_tom", "eval_parts_tom", "eval_sents_madeline", "eval_parts_madeline"]:
    #   print(file)
    #   if "sents_" in file:
    #     golddf = pd.read_csv(GOLD_SENT_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    #     golddf = golddf[golddf["y"]=="accept"]
    #   if "parts_" in file:
    #     golddf = pd.read_csv(GOLD_PART_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    #     golddf = golddf[golddf["y"]=="accept"]


    #   PREDS_PATH = pathlib.Path(PREDICTION_DIR + file + '.tsv')
    #   print(PREDS_PATH)
    #   predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","method","arg0","arg1","rel","answer","text"])
    #   write_tsv_for_scores_per_alg(predf, golddf, PREDICTION_STATS + file + '.tsv')

      # for metric in ["substring"]:
      #   for collapse in [True]:
      #     for consider_reverse in [True]:
      #         calc_original_accept_per_alg(predf, golddf, metric, consider_reverse=consider_reverse, collapse=collapse)

    # print("for task eval_sents_tom")
    # data_list = read_data(PREDICTION_DIR + "eval_sents_tom.jsonl")
    # calc_accept_rate_per_alg(data_list)
    # print("for task eval_parts_tom")
    # data_list = read_data(PREDICTION_DIR + "eval_parts_tom.jsonl")
    # calc_accept_rate_per_alg(data_list)
    # print("for task eval_sents_madeline")
    # data_list = read_data(PREDICTION_DIR + "eval_sents_madeline.jsonl")
    # calc_accept_rate_per_alg(data_list)
    # print("for task eval_parts_madeline")
    # data_list = read_data(PREDICTION_DIR + "eval_parts_madeline.jsonl")
    # calc_accept_rate_per_alg(data_list)
    




