import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, ie_eval
import pathlib
from pathlib import Path
import pandas as pd
"""
Usage:
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl 
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl --mech_effect_mode
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('--data_combo',
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
        gold_path = pathlib.Path(args.root) / 'gold_madeline' /  'mech_effect' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' 
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold_madeline' /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' 
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 


    GOLD_PATH = pathlib.Path(gold_path)
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]

    for file in os.listdir(str(pred_dir)):
      if file.startswith("run"):
        run_stat_path = stat_path / file
        run_stat_path.mkdir(parents=True, exist_ok=True)


        run_pred_dir = pred_dir / file /"pred.tsv"
        PREDS_PATH = pathlib.Path(run_pred_dir)

        
        #read predictions, place in dictionary

        prediction_dict = {}
        predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
        #check prediction label mapping matches the loaded gold file
        print(predf["rel"].unique())
        print(golddf["rel"].unique())
        prediction_dict[str(args.data_combo)] = predf[["id","arg0","arg1","rel","conf"]]
        
        res_list = []
        
        for k,v in prediction_dict.items():
            print ("****")
            if not len(v):
                print(k," -- NO PREDICTIONS -- ")
                continue
            #only try non-collapsed labels for relations that have it (i.e. ours and gold)
            if "rel" not in v.columns:
                collapse_opt = [True]
            else:
                collapse_opt = [False,True]
            for match_metric in ["jaccard","substring"]:
                for collapse in collapse_opt:

                    corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.5)
                    res = [k, precision, recall, F1, mech_effect, collapse, match_metric, 0.5]
                    res_list.append(res)
                    print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                    if match_metric == "jaccard":
                        corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.4)
                        res = [k, precision, recall, F1, mech_effect, collapse, match_metric, 0.4]
                        res_list.append(res)
                        print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                        corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.3)
                        res = [k, precision, recall, F1, mech_effect, collapse, match_metric, 0.3]
                        res_list.append(res)
                        print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))


            print ("****")

        stats_df = pd.DataFrame(res_list,columns =["model","P","R","F1","mech_effect_mode","collapse","match_mettric","threshold"])
        stats_path = run_stat_path / 'stats.tsv'
        stats_df.to_csv(stats_path,header=True,index=False, sep="\t")



