import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import depparse_base, allpairs_base, get_openie_predictor,get_srl_predictor,allenlp_base_relations, annotation_eval
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
    parser.add_argument('--name_list',
                        type=str,
                        help='name of annotators that we want to calc agreement(, seperated). the refrence is the first name',
                        default="madeline,sara,megan",
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        default='bio_annotations/annotations/',
                        help= 'path to where the annotations are saved',
                        required=False)


    args = parser.parse_args()
    name_list = args.name_list.split(',')
    assert len(name_list) > 1
    
    reference_name = name_list[0]
    
    refrence_file_name = "annotations_" + reference_name + '.tsv'
    gold_path = pathlib.Path(args.root) / 'tsvs' / refrence_file_name
    
    prediction_dict = {}
    for name in name_list[1:]:
        print(name)
        annotation_file_name = "annotations_" + name + '.tsv'
        anootation_path = pathlib.Path(args.root) / 'tsvs' / annotation_file_name

        stat_path = pathlib.Path(args.root) / 'stats' / name 
        stat_path.mkdir(parents=True, exist_ok=True)


        GOLD_PATH = pathlib.Path(gold_path)
        PREDS_PATH = pathlib.Path(anootation_path)

        golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
        golddf = golddf[golddf["y"]=="accept"]
        #read predictions, place in dictionary

        
        predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","y"])
        predf = predf[predf["y"]=="accept"]
        prediction_dict[name] = predf[["id","text","arg0","arg1","rel"]]
    
    #get results
    res_list = []
    
    for k,v in prediction_dict.items():
        print ("****")
        if not len(v):
            print(k," -- NO ANNOTATIONS -- ")
            continue
        #only try non-collapsed labels for relations that have it (i.e. ours and gold)
        if "rel" not in v.columns:
            collapse_opt = [True]
        else:
            collapse_opt = [False,True]
        for match_metric in ["jaccard","substring"]:
            for collapse in collapse_opt:

                accuracy = annotation_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.5)
                res = [k, accuracy, collapse, match_metric, 0.5]
                res_list.append(res)
                print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, accuracy, 0.5))
                if match_metric == "jaccard":
                    accuracy = annotation_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.4)
                    res = [k, accuracy, collapse, match_metric, 0.4]
                    res_list.append(res)
                    print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, accuracy, 0.4))
                    accuracy = annotation_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.3)
                    res = [k, accuracy, collapse, match_metric, 0.3]
                    res_list.append(res)
                    print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, accuracy, 0.3))


        print ("****")

    stats_df = pd.DataFrame(res_list,columns =["annotator","acc","collapse","match_mettric","threshold"])
    stats_path = stat_path / 'stats.tsv'
    stats_df.to_csv(stats_path,header=True,index=False, sep="\t")



