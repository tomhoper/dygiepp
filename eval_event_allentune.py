import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import read_coref_file, depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, ie_eval_event, ie_span_eval, ie_errors
import pathlib
from pathlib import Path
import pandas as pd
from tabulate import tabulate
"""
Usage:
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl 
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl --mech_effect_mode
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    # parser.add_argument('--pred_path',
    #                     type=Path,
    #                     help='root dataset folder, contains train/dev/test',
    #                     default="covid_anno_par",
    #                     required=True)
    parser.add_argument('--root',
                        type=Path,
                        default='/data/aida/covid_aaai',
                        required=False)
    parser.add_argument('--gold_path',
                        type=Path,
                        help='root dataset folder, contains train/dev/test',
                        default="/data/aida/covid_aaai/event-gold/",
                        required=False)
    parser.add_argument('--test_data',
                        action='store_true')
    
    parser.add_argument('--test_index',
                        type=int,
                        default=0)

    # parser.add_argument('--pred',
    #                     type=str,
    #                     help='path to predictions',
    #                     required=True)
    # parser.add_argument('--gold',
    #                     type=str,
    #                     help='path to gold labels',
    #                     required=False)

    args = parser.parse_args()
    if args.test_data:
        gold_path = pathlib.Path(args.gold_path) / 'test-gold.tsv'
    else:
        gold_path = pathlib.Path(args.gold_path) / 'dev-gold.tsv'

    coref = None

         
    if args.test_data:
      pred_dir = pathlib.Path(args.root) / 'predictions' / "events_sentence_correct" / 'mapped' / 'mech_effect'
    else:
      pred_dir = pathlib.Path(args.root) / 'predictions_dev' / "events_sentence_correct" / 'mapped' / 'mech_effect'
    
    
    GOLD_PATH = pathlib.Path(gold_path)
    PREDS_PATH = pathlib.Path(pred_dir)
    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","trigger","arg1"])

    best_run_index = 0
    best_run_score = 0

    prediction_dict = {}
    for file in os.listdir(str(pred_dir)):

      trail_strat_str = "run_"
      if args.test_data:
         trail_strat_str = trail_strat_str + str(args.test_index)
      
      if file.startswith(trail_strat_str):
        # run_stat_path = stat_path / file
        # run_stat_path.mkdir(parents=True, exist_ok=True)


        run_pred_dir = pred_dir / file /"pred.tsv"
        PREDS_PATH = pathlib.Path(run_pred_dir)

        
        #read predictions, place in dictionary
        run_index = file[4:file.index('_', 5)]
        # prediction_dict = {}

        try:
            predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","trigger","arg1","arg0_logit","trigger_logit","arg1_logit","arg0_softmax","trigger_softmax","arg1_softmax"])
        except:
            # print(str(run_index))
            continue
        # if len(predf) > 1000:
        #     continue
        # import pdb; pdb.set_trace()

        # print(str(run_index))
        prediction_dict[str("events") + '_run_' + run_index] = predf[["id","arg0","trigger","arg1"]]


    # get dep-parse relations and all pairs relations, place in prediction_dict
    # both baselines can use nnp, NER, or a combo
    # dep_relations = depparse_base(golddf,pair_type="NNP")
    # allpairs_relations = allpairs_base(golddf,pair_type="NNP")
    # prediction_dict["depparsennp"] = pd.DataFrame(dep_relations,columns=["id","arg0","arg1"])
    # prediction_dict["allpairsnnp"] = pd.DataFrame(allpairs_relations,columns=["id","arg0","arg1"])


    # get SRL relations and openIE relations, place in prediction_dict
    # predictor_ie = get_openie_predictor()
    # predictor_srl = get_srl_predictor()
    # srl_relations = allenlp_base_relations(predictor_srl,golddf)
    # ie_relations = allenlp_base_relations(predictor_ie,golddf)
    # prediction_dict["srl"] = pd.DataFrame(srl_relations,columns=["id","arg0","arg1"])
    # prediction_dict["openie"] = pd.DataFrame(ie_relations,columns=["id","arg0","arg1"])
    
    #get results
    res_list = []
    res_latex_list = []
    # import pdb; .set_trace()
    for k,v in prediction_dict.items():
        print(k)
        trial_score = 0.0
        print ("****")
        if not len(v):
            print(k," -- NO PREDICTIONS -- ")
            continue
        #only try non-collapsed labels for relations that have it (i.e. ours and gold)
        if "rel" not in v.columns:
            collapse_opt = [False]
        else:
            collapse_opt = [False,True]
        for match_metric in ["substring","exact"]:

        # for match_metric in ["rouge"]:
            for consider_reverse in [False, True]:
                # print(collapse)
        # for match_metric in ["substring"]:
                for collapse in collapse_opt:
                    th_opts = [1]
                    if match_metric == "rouge":
                        th_opts=[0.3]
                    if match_metric == 'jaccard':
                        th_opts = [0.3]
                    for th in th_opts:

                        # p_at_k = []
                        # k_th = [100, 150, 200, 50]
                        # # p_at_k = [100, 150, 200]
                        # for topK in k_th:
                        #     if "covid" not in k :
                        #         p_at_k.append(0)
                        #         continue
                        #     _, p, _, _ = ie_eval_event(v,golddf,coref=coref,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,topK=topK,consider_reverse=consider_reverse)
                        #     p_at_k.append(p)
                        
                        corr_pred, precision,recall, F1 = ie_eval_event(v,golddf,coref=coref,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,consider_reverse=consider_reverse)
                        trial_score += F1
                        res = [k, 100*round(precision,4), 100*round(recall,4), 100*round(F1,4), collapse, match_metric, th, consider_reverse]
                        # if collapse == True and consider_reverse == True:
                        res_latex = [k, match_metric, 100*round(precision,4), 100*round(recall,4), 100*round(F1,4)]
                        res_latex_list.append(res_latex)
                        res_list.append(res)
        if trial_score > best_run_score:
            best_run_score = trial_score
            best_run_index = k


       
    print(tabulate(res_list, headers =["model","P","R","F1","collapse","match_mettric","threshold", "consider_reverse"]))
    print ("****")
    if args.test_data == False:
            print("best run is " + str(best_run_index))
    # stats_df = pd.DataFrame(res_list,columns =["model","P","R","F1","collapse","match_mettric","threshold", "consider_reverse"])
    # stats_df_latex = pd.DataFrame(res_latex_list,columns =["model","match_metric","P","R","F1"])
    # stats_path = stat_path / 'stats.tsv'
    # print(str(stats_df_latex.to_latex()))
    # stats_df.to_csv(stats_path,header=True,index=False, sep="\t")

    # errors_path = stat_path / 'errors_non_collapse.tsv'
    # errors_collapse_path = stat_path / 'errors_collapse.tsv'

    # errors.to_csv(errors_path,header=True,index=False, sep="\t")
    # errors_collapse.to_csv(errors_collapse_path,header=True,index=False, sep="\t")

