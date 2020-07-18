import random
import argparse
import json
from eval_utils import depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, ie_eval
import pathlib
from pathlib import Path
import pandas as pd
import spacy

NLP = spacy.load("en_core_web_sm")
random.seed(100)

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


def convert_to_json(text, info):
  res = {}
  res["text"] = text
  res["meta"] = {}
  res["meta"]["section"] = "Abstract"
  res["meta"]["doc_key"] = info[3]
  res["method"] = info[0]
  
  tokens = process_paragraph(text)
  res["tokens"] = []

  seen_tokens = []
  ind_start = 0
  head_token_info = {}
  head_token_info["label"] = "ENTITY"
  # import pdb; pdb.set_trace()
  try:
    head_token_info["start"] = text.index(info[1].lstrip().lower()+" ")
    head_token_info["end"] = text.index(info[1].lstrip().lower()+" ") + len(info[1].lstrip().lower())
  except:
    head_token_info["start"] = text.index(info[1].lstrip().lower())
    head_token_info["end"] = text.index(info[1].lstrip().lower()) + len(info[1].lstrip().lower())

  child_token_info = {}
  child_token_info["label"] = "ENTITY"
  try:
    child_token_info["start"] = text.index(info[2].lstrip().lower()+" ")
    child_token_info["end"] = text.index(info[2].lstrip().lower()+" ") + len(info[2].lstrip().lower())
  except:
    child_token_info["start"] = text.index(info[2].lstrip().lower())
    child_token_info["end"] = text.index(info[2].lstrip().lower()) + len(info[2].lstrip().lower())


  for i in range(len(tokens)):
    tok = tokens[i]
    tok_info = {}
    tok_info["text"] = tok
    tok_info["start"] = text.index(tok, ind_start)
    tok_info["end"] = text.index(tok, ind_start) + len(tok)
    
    if tok_info["start"] == head_token_info["start"]:
      head_token_info["token_start"] = i
    if tok_info["end"] == head_token_info["end"]:
      head_token_info["token_end"] = i
    if tok_info["start"] == child_token_info["start"]:
      child_token_info["token_start"] = i
    if tok_info["end"] == child_token_info["end"]:
      child_token_info["token_end"] = i


    # if tok not in seen_tokens:
    #   seen_tokens.append(tok)
    tok_info["id"] = i
    tok_info["disabled"] = False
    res["tokens"].append(tok_info)
    ind_start += len(tok)
    if ind_start < len(text) and text[ind_start] == " ":
      ind_start += 1
  res["_view_id"] = "relations"
  
  res["spans"] = []
  res["spans"].append(head_token_info)
  res["spans"].append(child_token_info)

  res["relations"] = []


  relations_info = {}
  relations_info["label"] = "USED-TO"
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('--data_combo_list',
                        type=str,
                        help='root dataset folder, contains train/dev/test',
                        default="covid_anno_par",
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        default='/data/aida/covid_clean',
                        required=False)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--abstract_count',
                        type=int,
                        default=10,
                        required=True)
    
    args = parser.parse_args()
    mech_effect = args.mech_effect_mode

    data_sets = args.data_combo_list.split(',')
    for data_combo in data_sets:
      if args.mech_effect_mode == True:
          gold_path = pathlib.Path(args.root) / 'gold' /  'mech_effect' / 'gold_par.tsv'
          pred_dir = pathlib.Path(args.root) / 'predictions' / data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
          stat_path = pathlib.Path(args.root) / 'stats' / data_combo / 'mapped' / 'mech_effect/' 

      if args.mech_effect_mode == False:
          gold_path = pathlib.Path(args.root) / 'gold' /  'mech' / 'gold_par.tsv'
          pred_dir = pathlib.Path(args.root) / 'predictions' / data_combo / 'mapped' / 'mech' / "pred.tsv"
          stat_path = pathlib.Path(args.root) / 'stats' / data_combo / 'mapped' / 'mech/' 
      
      GOLD_PATH = pathlib.Path(gold_path)
      PREDS_PATH = pathlib.Path(pred_dir)

      #read predictions, place in dictionary

      prediction_dict = {}
      predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
      predf["id"] = predf["id"].str.replace(r'[+]+$','')
      prediction_dict[str(data_combo)] = predf[["id","text","arg0","arg1","rel","conf"]]

    # get dep-parse relations and all pairs relations, place in prediction_dict
    # both baselines can use nnp, NER, or a combo
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    golddf["id"] = golddf["id"].str.replace(r'[+]+$','')

    dep_relations = depparse_base(golddf,pair_type="NNP",four_col=True)
    allpairs_relations = allpairs_base(golddf,pair_type="NNP",four_col=True)
    # prediction_dict["depparsennp"] = pd.DataFrame(dep_relations,columns=["id","text","arg0","arg1"])
    # prediction_dict["allpairsnnp"] = pd.DataFrame(allpairs_relations,columns=["id","text","arg0","arg1"])


    #get SRL relations and openIE relations, place in prediction_dict
    # predictor_ie = get_openie_predictor()
    predictor_srl = get_srl_predictor()
    srl_relations = allenlp_base_relations(predictor_srl,golddf,four_col=True)
    # ie_relations = allenlp_base_relations(predictor_ie,golddf,four_col=True)
    prediction_dict["srl"] = pd.DataFrame(srl_relations,columns=["id","text","arg0","arg1"])
    # prediction_dict["openie"] = pd.DataFrame(ie_relations,columns=["id","text","arg0","arg1"])
    
    interset_ids = []
    for k,v in prediction_dict.items():
      l1 = [i for i in v["id"].drop_duplicates()]
      if interset_ids == []:
        interset_ids = l1
      else:
        interset_ids = (list)(set(interset_ids).intersection(set(l1)))
    random.shuffle(interset_ids)

    output_file = open("human_annotations.jsonl", "w")
    output_file_tsv = open("human_annotations.tsv", "w")
    output_file_tsv.write("method\targ0\targ1\tid\ttext\n")
    # import pdb; pdb.set_trace()
    for ind in interset_ids[:args.abstract_count]:
      per_text_mapping = {}
      for k,v in prediction_dict.items():
        v = v.set_index("id")
        v.loc[ind]
        for row in v.iterrows():
          row[1]["text"] = row[1]["text"].lower()
          if row[1]["text"] not in per_text_mapping:
            per_text_mapping[row[1]["text"]] = []
            # import pdb; pdb.set_trace()
          per_text_mapping[row[1]["text"]].append((k, row[1]["arg0"], row[1]["arg1"], row[0]))

      # import pdb; pdb.set_trace()
      for text in per_text_mapping:
        res = per_text_mapping[text]
        random.shuffle(res)

        for r in res:
          d = convert_to_json(text, r)
          if d != {}:
            output_file_tsv.write('\t'.join(r) + '\t' + text + '\n')
            json.dump(d, output_file)
            output_file.write("\n")
        




