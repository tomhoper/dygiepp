import argparse
import json
import os
import shutil
import subprocess
from typing import Any, Dict
import sys



def eval_model_preds(gold_path, pred_path):
    golddf = pd.read_csv(gold_path, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]

    #read predictions, place in dictionary
    predf = pd.read_csv(pred_path, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    

    prediction_dict = {}
    prediction_dict["model preds"] = predf[["id","arg0","arg1"]]

    #get results
    for k,v in prediction_dict.items():
        print ("****")
        if not len(v):
            print(k," -- NO PREDICTIONS -- ")
            continue
        for match_metric in ["jaccard","substring"]:
            corr_pred, precision,recall, F1 = eval(v,golddf,match_metric=match_metric,jaccard_thresh=0.3)
            print('model: {0} metric: {1} precision:{2} recall {3} f1: {4}'.format(k, match_metric, precision,recall, F1))
        print ("****")


if __name__ == '__main__':

    parser = argparse.ArgumentParser() 

    parser.add_argument('--pred_path',
                        type=str,
                        help='path to save the predictions',
                        required=True)

    args = parser.parse_args()

    
    from allennlp.common.params import Params
    from eval_utils import *
    eval_model_preds("gold_par.tsv", args.pred_path + "pred.tsv")
