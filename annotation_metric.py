import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import annotation_eval, diff, ie_eval_agreement
import pathlib
from pathlib import Path
import pandas as pd
from tabulate import tabulate


def agreement_accuracy_calculation(prediction_dict, golddf):
    res_list = {}
    for k,v in prediction_dict.items():
        res_list[k] = []
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
                res_list[k].append(res)
                print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, round(accuracy,2), 0.5))
                if match_metric == "jaccard":
                    accuracy = annotation_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.4)
                    res = [k, accuracy, collapse, match_metric, 0.4]
                    res_list[k].append(res)
                    # print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, round(accuracy,2), 0.4))
                    accuracy = annotation_eval(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.3)
                    res = [k, accuracy, collapse, match_metric, 0.3]
                    res_list[k].append(res)
                    print('annotator: {0} collapsed: {1} metric: {2} accuracy:{3} threshold:{4}'.format(k, collapse, match_metric, round(accuracy,2), 0.3))

    return res_list


def agreement_calculation(prediction_dict, golddf):
    res_list = {}
    for k,v in prediction_dict.items():
        res_list[k] = []
        print ("****")
        if not len(v):
            print(k," -- NO ANNOTATIONS -- ")
            continue
        #only try non-collapsed labels for relations that have it (i.e. ours and gold)
        if "rel" not in v.columns:
            collapse_opt = [True]
        else:
            collapse_opt = [False,True]
        for match_metric in ["jaccard", "rouge","substring"]:
            for collapse in collapse_opt:
                th_opts = [1]
                if match_metric == "rouge":
                    th_opts=[0.5]
                if match_metric == 'jaccard':
                    th_opts = [0.3, 0.5]
                for th in th_opts:

                    corr_pred, precision,recall, F1 = ie_eval_agreement(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=th,consider_reverse=False)
                    res = [k, round(precision,2), round(recall,2), round(F1,2), collapse, match_metric, th]
                    res_list[k].append(res)

        print(tabulate(res_list[k], headers=["name","P","R","F1","collapse","match_mettric","threshold"]))  
        print ("****")
    return res_list


def get_agreement_on_initial_annotations(root):
    print("calculating agreement on initial round of annotations ")
    name_list = ["sara", "megan", "madeline"]
    for i in range(len(name_list)):
        print ("for name "  + (name_list[i]))
        prediction_dict = {}
        for j in range(i+1, len(name_list)):
            name1 = name_list[i]
            name2 = name_list[j]
            file1_name = "annotations_" + name1 + '.tsv'
            file2_name = "annotations_" + name2 + '.tsv'
            gold_path = pathlib.Path(args.root) / 'annotations' / 'tsvs' / file1_name
            annotated_path = pathlib.Path(args.root) / 'annotations' / 'tsvs' / file2_name
            GOLD_PATH = pathlib.Path(gold_path)
            PREDS_PATH = pathlib.Path(annotated_path)
            golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y","annotator"])
            golddf = golddf[golddf["y"]=="accept"]

            predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","y", "annotator"])
            predf = predf[predf["y"]=="accept"]
            prediction_dict[name2] = predf[["id","text","arg0","arg1","rel"]]

        res_list = agreement_calculation(prediction_dict, golddf)
        for k,v in prediction_dict.items():
            print ("****")
            stat_file_name = name1 + "_" + k + '.txt'
            stat_path = pathlib.Path(args.root) / 'stats' / 'initial_annotations' /  stat_file_name
            stat_path.mkdir(parents=True, exist_ok=True)
            stats_df = pd.DataFrame(res_list[k],columns =["name","P","R","F1","collapse","match_mettric","threshold"])
            stats_path = stat_path / 'stats.tsv'
            stats_df.to_csv(stats_path,header=True,index=False, sep="\t")


def get_agreement_on_after_self_correction(root):

    #TODO there is a bug here. what is madeline corrects the intersection of megan and sara again 
    print("calculating agreement after self correction ")
    name_list = ["tom", "madeline"]

    for i in range(len(name_list)):
        print ("for name "  + (name_list[i]))
        prediction_dict = {}
        for j in range(i+1, len(name_list)):
            name1 = name_list[i]
            name2 = name_list[j]
            # file1_name = "annotations_" + name1 + '.tsv'
            # file2_name = "corrections_" + name2 + '.tsv'
            # gold_path = pathlib.Path(args.root) /'annotations' / 'tsvs' / file1_name
            # annotated_path = pathlib.Path(args.root) / 'corrections_old' / 'tsvs' / file2_name
            gold_path = "bio_annotations/validations/madeline_tom.tsv"
            annotated_path = "bio_annotations/validations/input_madeline_tom.tsv"
            file1_name = "corrections_" + name1 + '.tsv'
            file2_name = "corrections_" + name2 + '.tsv'
            gold_path = pathlib.Path(args.root) / 'self_corrections' / 'tsvs' / file1_name
            annotated_path = pathlib.Path(args.root) / 'self_corrections' / 'tsvs' / file2_name


            GOLD_PATH = pathlib.Path(gold_path)
            PREDS_PATH = pathlib.Path(annotated_path)
            golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y","annotator"])
            golddf = golddf[golddf["y"]=="accept"]

            predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","y", "annotator"])
            predf = predf[predf["y"]=="accept"]
            prediction_dict[name2] = predf[["id","text","arg0","arg1","rel"]]

        res_list = agreement_calculation(prediction_dict, golddf)
        for k,v in prediction_dict.items():
            print ("****")
            stat_file_name = name1 + "_" + k + '.txt'
            stat_path = pathlib.Path(args.root) / 'stats' / 'initial_annotations' /  stat_file_name
            stat_path.mkdir(parents=True, exist_ok=True)
            stats_df = pd.DataFrame(res_list[k],columns =["name","P","R","F1","collapse","match_mettric","threshold"])
            stats_path = stat_path / 'stats.tsv'
            stats_df.to_csv(stats_path,header=True,index=False, sep="\t")


if __name__ == '__main__':

    parser = argparse.ArgumentParser() 
    parser.add_argument('--name_list',
                        type=str,
                        help='name of annotators that we want to calc agreement(, seperated). the refrence is the first name',
                        default="madeline,sara,megan",
                        required=False)

    parser.add_argument('--root',
                        type=Path,
                        default='bio_annotations/',
                        help= 'path to where the annotations are saved',
                        required=False)

    args = parser.parse_args()

    #report part 1: for all annotator print cross agreement on initial annotation
    # get_agreement_on_initial_annotations(args.root)

    #report part 2: for all annotator print cross agreement after one round of correction

    get_agreement_on_after_self_correction(args.root)

    #get percentage of tome annotations that madeline chaneged 
    # golddf = pd.read_csv("bio_annotations/validations/madeline_tom.tsv", sep="\t",header=None, names=["id","text","arg0","arg1","rel","y","annotator"])
    # # import pdb; pdb.set_trace()
    # golddf = golddf[golddf["y"]=="accept"]
    
    # predf = pd.read_csv("bio_annotations/validations/input_madeline_tom.tsv", sep="\t",names=["id","text","arg0","arg1","rel","y", "annotator"])
    # predf = predf[predf["y"]=="accept"]
    # diff(predf,golddf, collapse=False,output_diff_path="non_collapse_madeline_changes.tsv")

    # golddf = pd.read_csv("bio_annotations/validations/madeline_tom.tsv", sep="\t",header=None, names=["id","text","arg0","arg1","rel","y","annotator"])
    # # import pdb; pdb.set_trace()
    # golddf = golddf[golddf["y"]=="accept"]
    
    # predf = pd.read_csv("bio_annotations/validations/input_madeline_tom.tsv", sep="\t",names=["id","text","arg0","arg1","rel","y", "annotator"])
    # predf = predf[predf["y"]=="accept"]
    # diff(predf,golddf, collapse=True, output_diff_path="collapse_madeline_changes.tsv")

    # get_agreement_on_after_self_correction(args.root)

    
