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

"""
Usage:
python eval_metric.py --pred ../covidpreds/ --gold UnifiedData/covid_anno_par/gold/mech/
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

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"


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
    # assert predf["rel"].unique()[0] == golddf["rel"].unique()[0]
    prediction_dict["model preds"] = predf[["id","arg0","arg1"]]


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
    for k,v in prediction_dict.items():
        print ("****")
        if not len(v):
            print(k," -- NO PREDICTIONS -- ")
            continue
        for match_metric in ["jaccard","substring"]:
            corr_pred, precision,recall, F1 = ie_eval(v,golddf,match_metric=match_metric,jaccard_thresh=0.5)
            print('model: {0} metric: {1} precision:{2} recall {3} f1: {4}'.format(k, match_metric, precision,recall, F1))
        print ("****")


