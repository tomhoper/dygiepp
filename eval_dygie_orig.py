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
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl 
python eval_metric.py --root ../coviddata --data_combo scierc_chemprot_srl --mech_effect_mode
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser() 

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
        # pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
        # stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect' / 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech' / 'gold_par.tsv'
        # pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"
        # stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech' / 
        stat_path = pathlib.Path(args.root) / 'stats'

    pred_dir = "/data/aida/covid_clean/predictions/pred_dygie_orig_scierc.tsv"
    stat_path.mkdir(parents=True, exist_ok=True)

    stats_output_file = open(str(stat_path) +'/stats_dygie_original_scierc.tsv', 'w')
    stats_output_file.write("alg_name\tP\tR\tF1\tcollapse\tsimilarity_metric\tjaccard-th\n")

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
    assert len(predf["rel"].unique()) == len(golddf["rel"].unique())
    prediction_dict['dygie_orig'] = predf[["id","arg0","arg1","rel","conf"]]


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
        #only try non-collapsed labels for relations that have it (i.e. ours and gold)
        if "rel" not in v.columns:
            collapse_opt = [True]
        else:
            collapse_opt = [False,True]
        for match_metric in ["jaccard","substring"]:
            for collapse in collapse_opt:
                corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.33)
                res = [k, precision, recall, F1, collapse, match_metric, 0.33]
                # stats_output_file.write('\t'.join(res) + '\n')
                print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5}'.format(k, collapse, match_metric, precision,recall, F1))
        print ("****")


