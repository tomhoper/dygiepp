import argparse
import json
import os   
import shutil
import subprocess
from typing import Any, Dict
import sys
import pandas as pd
from eval_utils import get_matching_pairs
import pathlib
from pathlib import Path
import pandas as pd


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


    args = parser.parse_args()

    if args.mech_effect_mode == True:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech_effect' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech_effect/' 

    if args.mech_effect_mode == False:
        gold_path = pathlib.Path(args.root) / 'gold' /  'mech' / 'gold_par.tsv'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech' / "pred.tsv"
        stat_path = pathlib.Path(args.root) / 'stats' / args.data_combo / 'mapped' / 'mech/' 

    GOLD_PATH = pathlib.Path(gold_path)
    PREDS_PATH = pathlib.Path(pred_dir)
    stat_path.mkdir(parents=True, exist_ok=True)

    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]
    #read predictions, place in dictionary

    prediction_dict = {}
    predf = pd.read_csv(PREDS_PATH, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    #check prediction label mapping matches the loaded gold file
    print(predf["rel"].unique())
    print(golddf["rel"].unique())
    assert len(predf["rel"].unique()) == len(golddf["rel"].unique())
    prediction_dict[str(args.data_combo)] = predf[["id","arg0","arg1","rel","conf"]]

    for k,v in prediction_dict.items():
        if not len(v):
            continue
        #only try non-collapsed labels for relations that have it (i.e. ours and gold)
        if "rel" not in v.columns:
            collapse_opt = [True]
        else:
            collapse_opt = [False,True]
        for match_metric in ["jaccard","substring"]:
            for collapse in collapse_opt:
                mappings = get_matching_pairs(v,golddf,collapse = collapse, match_metric=match_metric,jaccard_thresh=0.5)























