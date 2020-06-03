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
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        help='./',
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

    if args.mech_effect_mode == True:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech_effect' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 

    stat_path.mkdir(parents=True, exist_ok=True)



    GOLD_PATH = pathlib.Path(gold_path)
    PREDS_PATH = pathlib.Path(pred_dir)

    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    golddf["id"] = golddf["id"].str.replace(r'[+]+$','')
    #read predictions, place in dictionary

    prediction_dict = {}
    predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    predf["id"] = predf["id"].str.replace(r'[+]+$','')
    #check prediction label mapping matches the loaded gold file
    print(predf["rel"].unique())
    print(golddf["rel"].unique())
    assert len(predf["rel"].unique()) == len(golddf["rel"].unique())
    prediction_dict[str(args.data_combo)] = predf[["id","arg0","arg1","rel","conf"]]


    #get dep-parse relations and all pairs relations, place in prediction_dict
    #both baselines can use nnp, NER, or a combo
    dep_relations = depparse_base(golddf,pair_type="NNP")
    allpairs_relations = allpairs_base(golddf,pair_type="NNP")
    prediction_dict["depparsennp"] = pd.DataFrame(dep_relations,columns=["id","arg0","arg1"])
    prediction_dict["allpairsnnp"] = pd.DataFrame(allpairs_relations,columns=["id","arg0","arg1"])


    #get SRL relations and openIE relations, place in prediction_dict
    predictor_ie = get_openie_predictor()
    predictor_srl = get_srl_predictor()
    srl_relations = allenlp_base_relations(predictor_srl,golddf)
    ie_relations = allenlp_base_relations(predictor_ie,golddf)
    prediction_dict["srl"] = pd.DataFrame(srl_relations,columns=["id","arg0","arg1"])
    prediction_dict["openie"] = pd.DataFrame(ie_relations,columns=["id","arg0","arg1"])
    
    #get results
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
                res = [k, precision, recall, F1, collapse, match_metric, 0.5]
                res_list.append(res)
                print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                if match_metric == "jaccard":
                    corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.4)
                    res = [k, precision, recall, F1, collapse, match_metric, 0.4]
                    res_list.append(res)
                    print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
                    corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.3)
                    res = [k, precision, recall, F1, collapse, match_metric, 0.3]
                    res_list.append(res)
                    print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))


        print ("****")

    stats_df = pd.DataFrame(res_list,columns =["model","P","R","F1","collapse","match_mettric","threshold"])
    stats_path = stat_path / 'stats.tsv'
    stats_df.to_csv(stats_path,header=True,index=False, sep="\t")



