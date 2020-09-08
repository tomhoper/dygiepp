import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import read_coref_file, depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, ie_eval, ie_span_eval, ie_errors
import pathlib
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


"""
Usage:
conda activate /home/aida/miniconda3/envs/covid_eval
python eval_metric.py --root ../covid_aaai/ --data_combo covid_anno_par_madeline_sentences_matchcd --mech_effect_mode --gold_combo gold_madeline_sentences_matchcd --open 
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('--data_combo',
                        type=str,
                        help='root dataset folder, contains train/dev/test',
                        default="covid_anno_par",
                        required=True)

    parser.add_argument('--gold_combo',
                        type=Path,
                        help='root dataset folder, contains train/dev/test',
                        default="covid_anno_par",
                        required=True)


    parser.add_argument('--root',
                        type=Path,
                        default='../coviddata',
                        required=True)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--open',
                        action='store_true')

    # parser.add_argument('--pred',
    #                     type=str,
    #                     help='path to predictions',
    #                     required=True)
    # parser.add_argument('--gold',
    #                     type=str,
    #                     help='path to gold labels',
    #                     required=False)

    args = parser.parse_args()
    mech_effect = args.mech_effect_mode
    if args.mech_effect_mode == True:
        gold_path = pathlib.Path(args.root) / args.gold_combo  /  'mech_effect' / 'gold_par.tsv'
        
    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / args.gold_combo  /  'mech' / 'gold_par.tsv'
        
    
    coref = None
    GOLD_PATH = pathlib.Path(gold_path)
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    #read predictions, place in dictionary
    prediction_dict = {}

    data_combos = args.data_combo.split(',')
    for combo in data_combos:
      if combo == "scierc":
        pred_dir = pathlib.Path(args.root) / 'predictions'/ 'scierc_pretrained'/ 'covid_anno_par_madeline_sentences_matchcd' / 'mapped' / 'mech_effect' / "pred.tsv"
        print(str(pred_dir))
      else:
        if args.mech_effect_mode == True:
          pred_dir = pathlib.Path(args.root) / 'predictions'/ combo / 'mapped' / 'mech_effect' / "pred.tsv"
         
        if args.mech_effect_mode == False:
          pred_dir = pathlib.Path(args.root) / 'predictions' / combo / 'mapped' / 'mech' / "pred.tsv"

      
      PREDS_PATH = pathlib.Path(pred_dir)
         
      predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
      prediction_dict[str(combo)] = predf[["id","arg0","arg1","rel","conf"]]

      #get results for charts :
      p_at_kres = {}
      F1_at_th_res = {}
      res_list = []
      res_latex_list = []
      res_span_list = []
      match_metric = "rouge"
      th = 0.5
      collapse = True
      consider_reverse = True
      transivity = True


    for k,v in prediction_dict.items():
          print ("****")
          if not len(v):
              print(k," -- NO PREDICTIONS -- ")
              continue
       

          p_at_k = []
          F1_at_th = []
          for topK in range(1,100):
              _, p, _, _ = ie_eval(v,golddf,transivity=transivity,coref=coref,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,topK=topK,consider_reverse=consider_reverse)
              print(p)
              p_at_k.append(p)
          for i in range(1,100):
            th = float(i)/100
            corr_pred, precision,recall, F1 = ie_eval(v,golddf,transivity=transivity,coref=coref,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,consider_reverse=consider_reverse)
            F1_at_th.append(F1)

          F1_at_th_res[k] = F1_at_th
          p_at_kres[k] = p_at_k

    # Data
    y_list = []
    y_names = []
    for k in F1_at_th_res:
      y_list.append(F1_at_th_res[k])
      y_names.append(k)
    df=pd.DataFrame({'x': range(1,100), 'y1': y_list[0], 'y2': y_list[1]})
    df.to_csv("F1_at_th_res.tsv",header=False,index=False, sep="\t")

    y_list = []
    y_names = []
    for k in p_at_kres:
      y_list.append(p_at_kres[k])
      y_names.append(k)
    df=pd.DataFrame({'x': range(1,100), 'y1': y_list[0], 'y2': y_list[1]})
    df.to_csv("p_at_kres.tsv",header=False,index=False, sep="\t")
    # multiple line plot
    # plt.plot( 'x', 'y1', data=df, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=3)
    # plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=3)
   




