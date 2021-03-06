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
    parser.add_argument('--gold_combo',
                        type=Path,
                        help='root dataset folder, contains train/dev/test',
                        default="gold_madeline_sentences_matchcd",
                        required=True)
    parser.add_argument('--root',
                        type=Path,
                        default='../coviddata',
                        required=True)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--test_data',
                        action='store_true')
    
    parser.add_argument('--test_index',
                        type=int,
                        default=0)

    args = parser.parse_args()
    mech_effect = args.mech_effect_mode
    if args.mech_effect_mode == True:
        gold_path = pathlib.Path(args.root) / args.gold_combo /  'mech_effect' / 'gold_par.tsv'
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 
        if args.test_data == True:
            pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' 
        else:
            pred_dir = pathlib.Path(args.root) / 'predictions_dev' / args.data_combo / 'mapped' / 'mech_effect' 



    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / args.gold_combo /  'mech' / 'gold_par.tsv'
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 
        if args.pred_data == True:
            pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' 
        else:
            pred_dir = pathlib.Path(args.root) / 'predictions_dev' / args.data_combo / 'mapped' / 'mech' 
        

    GOLD_PATH = pathlib.Path(gold_path)
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    best_run_index = 0
    best_run_score = 0

    for file in os.listdir(str(pred_dir)):
      trail_strat_str = "run_"
      if args.test_data:
         trail_strat_str = trail_strat_str + str(args.test_index)
      
      if file.startswith(trail_strat_str):

        run_stat_path = stat_path / file
        run_stat_path.mkdir(parents=True, exist_ok=True)


        run_pred_dir = pred_dir / file /"pred.tsv"
        PREDS_PATH = pathlib.Path(run_pred_dir)

        
        #read predictions, place in dictionary
        run_index = file[4:file.index('_', 5)]
        prediction_dict = {}
        try:
            predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
        except:
            continue
        if len(predf) > 1000:
            continue

        #check prediction label mapping matches the loaded gold file
        print(predf["rel"].unique())
        print(golddf["rel"].unique())
        prediction_dict[str(args.data_combo) + '_run_' + run_index] = predf[["id","arg0","arg1","rel","conf"]]
        
        res_list = []
        
        

        for k,v in prediction_dict.items():
            trial_score = 0

            print(k)
            try:
                print ("****")
                if not len(v):
                    print(k," -- NO PREDICTIONS -- ")
                    continue
                #only try non-collapsed labels for relations that have it (i.e. ours and gold)
                if "rel" not in v.columns:
                    collapse_opt = [True]
                else:
                    collapse_opt = [False,True]
                for match_metric in ["exact","substring"]:
                    for collapse in collapse_opt:

                        corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.5,consider_reverse=True)
                        res = [k, precision, recall, F1, mech_effect, collapse, match_metric, 0.5]
                        trial_score += F1
                        res_list.append(res)
                        print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                        if match_metric == "jaccard":
                            corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.4,consider_reverse=True)
                            res = [k, precision, recall, F1, mech_effect, collapse, match_metric, 0.4]
                            res_list.append(res)
                            print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                            corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.3,consider_reverse=True)
 
                if trial_score > best_run_score:
                    best_run_score = trial_score
                    best_run_index = k

            except:
                print(k)
            print ("****")

        stats_df = pd.DataFrame(res_list,columns =["model","P","R","F1","mech_effect_mode","collapse","match_mettric","threshold"])
        stats_path = run_stat_path / 'stats.tsv'
        stats_df.to_csv(stats_path,header=True,index=False, sep="\t")
        if args.test_data == False:
            print("best run is " + best_run_index)

