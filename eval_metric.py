import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, ie_eval, ie_span_eval
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
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold_madeline' /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 

    stat_path.mkdir(parents=True, exist_ok=True)


    GOLD_PATH = pathlib.Path(gold_path)
    PREDS_PATH = pathlib.Path(pred_dir)

    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    #read predictions, place in dictionary

    prediction_dict = {}
    predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    #check prediction label mapping matches the loaded gold file
    print(predf["rel"].unique())
    print(golddf["rel"].unique())
    # assert len(predf["rel"].unique()) == len(golddf["rel"].unique())
    prediction_dict[str(args.data_combo)] = predf[["id","arg0","arg1","rel","conf"]]


    # get dep-parse relations and all pairs relations, place in prediction_dict
    # both baselines can use nnp, NER, or a combo
    # dep_relations = depparse_base(golddf,pair_type="NNP")
    # allpairs_relations = allpairs_base(golddf,pair_type="NNP")
    # prediction_dict["depparsennp"] = pd.DataFrame(dep_relations,columns=["id","arg0","arg1"])
    # prediction_dict["allpairsnnp"] = pd.DataFrame(allpairs_relations,columns=["id","arg0","arg1"])


    #get SRL relations and openIE relations, place in prediction_dict
    # predictor_ie = get_openie_predictor()
    # predictor_srl = get_srl_predictor()
    # srl_relations = allenlp_base_relations(predictor_srl,golddf)
    # ie_relations = allenlp_base_relations(predictor_ie,golddf)
    # prediction_dict["srl"] = pd.DataFrame(srl_relations,columns=["id","arg0","arg1"])
    # prediction_dict["openie"] = pd.DataFrame(ie_relations,columns=["id","arg0","arg1"])
    
    #get results
    res_list = []
    res_span_list = []

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
        for match_metric in ["jaccard","substring","exact"]:
            for collapse in collapse_opt:
                th_opts = [1]
                if match_metric == 'jaccard':
                    th_opts = [0.3, 0.4, 0.5]
                for th in th_opts:
                    k_th = [100, 150, 200]
                    p_at_k = []
                    for topK in k_th:
                        _, p, _, _ = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,topK=topK)
                        p_at_k.append(p)


                    corr_pred, precision,recall, F1 = ie_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=th)
                    span_corr_pred, span_precision,span_recall, span_F1 = ie_span_eval(v,golddf, match_metric=match_metric,jaccard_thresh=th)
                    res = [k, precision, recall, F1, p_at_k[0],p_at_k[1],p_at_k[2] , mech_effect, collapse, match_metric, th]
                    res_span = [k, span_precision, span_recall, span_F1, match_metric, th]
                    res_list.append(res)
                    res_span_list.append(res_span)
                    print('model: {0} collapsed: {1} metric: {2} precision:{3} recall {4} f1: {5} P@{12}: {6} P@{13}: {7} P@{14}: {8} span_presicion: {9} span_recall: {10} span_F1: {11}'.format(k, collapse, match_metric, precision,recall, F1, p_at_k[0],p_at_k[1],p_at_k[2], span_precision,span_recall, span_F1, k_th[0], k_th[1], k_th[2]))

        print ("****")

    stats_df = pd.DataFrame(res_list,columns =["model","P","R","F1","P@100","P@150","P@200","mech_effect_mode","collapse","match_mettric","threshold"])
    stats_path = stat_path / 'stats.tsv'
    stats_df.to_csv(stats_path,header=True,index=False, sep="\t")



