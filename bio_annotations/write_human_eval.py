import random
import argparse
import json
from eval_utils import depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, convert_to_json
import pathlib
from pathlib import Path
import pandas as pd
import spacy

random.seed(100)


if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('--data_combo',
                        type=str,
                        help='root dataset folder, contains train/dev/test',
                        default="covid_anno_par",
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        default='/data/aida/covid_aaai',
                        required=False)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--abstract_count',
                        type=int,
                        default=10,
                        required=True)

    parser.add_argument('--gold_combo',
                        type=str,
                        help='root dataset folder, contains train/dev/test',
                        default="covid_anno_par",
                        required=True)
    
    args = parser.parse_args()
    mech_effect = args.mech_effect_mode

    prediction_dict = {}

    if args.mech_effect_mode == True:
        gold_path = pathlib.Path(args.root) / args.gold_combo /  'mech_effect' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / args.gold_combo /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 
    
    GOLD_PATH = pathlib.Path(gold_path)
    PREDS_PATH = pathlib.Path(pred_dir)

    #read predictions, place in dictionary
    
    predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    predf["id"] = predf["id"].str.replace(r'[+]+$','')
    prediction_dict[str(args.data_combo)] = predf[["id","text","arg0","arg1","rel","conf"]]
    print("len of predictions for " + args.data_combo +  " is " + str(len(predf)))

    # get dep-parse relations and all pairs relations, place in prediction_dict
    # both baselines can use nnp, NER, or a combo
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    golddf["id"] = golddf["id"].str.replace(r'[+]+$','')


    #get SRL relations and openIE relations, place in prediction_dict
    predictor_ie = get_openie_predictor()
    predictor_srl = get_srl_predictor()
    srl_relations = allenlp_base_relations(predictor_srl,golddf,four_col=True)
    ie_relations = allenlp_base_relations(predictor_ie,golddf,four_col=True)
    prediction_dict["srl"] = pd.DataFrame(srl_relations,columns=["id","text","arg0","arg1"])
    print("openie relation count: " + str(len(ie_relations)))
    print("srl relation count: " + str(len(srl_relations)))

    prediction_dict["openie"] = pd.DataFrame(ie_relations,columns=["id","text","arg0","arg1"])
    
    interset_ids = []
    for k,v in prediction_dict.items():
      l1 = [i for i in v["id"].drop_duplicates()]
      if interset_ids == []:
        interset_ids = l1
      else:
        interset_ids = (list)(set(interset_ids).intersection(set(l1)))
    
    random.shuffle(interset_ids)
    print(len(interset_ids))
    
    output_file = open("human_annotations.jsonl", "w")
    output_file_tsv = open("human_annotations.tsv", "w")
    output_file_tsv.write("method\targ0\targ1\tid\ttext\n")
    # import pdb; pdb.set_trace()
    count = 0
    for ind in interset_ids[:args.abstract_count]:
      per_text_mapping = {}
      for k,v in prediction_dict.items():

        v = v.set_index("id",inplace=False)
        v = v.loc[[ind]]
        count += len(v)
        
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

        for r in range(len(res)):
          d = convert_to_json(text + "::V" + str(r), res[r])
          if d != {}:
            output_file_tsv.write('\t'.join(res[r]) + '\t' + text + '\n')
            json.dump(d, output_file)
            output_file.write("\n")
    print(count)  




