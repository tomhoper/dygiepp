import argparse
import json
import os
import shutil
import subprocess
from typing import Any, Dict
import sys
from dygie_visualize_util import Dataset
import pathlib
from pathlib import Path

"""
Usage

python predict.py --root ../coviddata --data_combo scierc_chemprot_srl 
python predict.py --root ../coviddata --data_combo scierc_chemprot_srl --mech_effect_mode


"""



def get_doc_key_info(ds):
  doc_info_conf_iter = {}
  for doc in ds:
    doc_key = doc._doc_key
    for sent in doc:
      sent_text = " ".join(sent.text)
      for rel in sent.relations:
        arg0 = " ".join(rel.pair[0].text)
        arg1 = " ".join(rel.pair[1].text)
        data_key = (doc_key, sent_text, arg0, arg1, rel.label)
        doc_info_conf_iter[data_key] = rel.score
  return doc_info_conf_iter


def prediction_to_tsv(ds, output_file_name):  
  doc_info = get_doc_key_info(ds)
  print(len(doc_info))
  output_file = open(output_file_name, "w")
  for key in doc_info:
    conf0 = str(doc_info[key])
    output_file.write(key[0] + '\t' + key[1] + '\t' + key[2] + '\t' + key[3] + '\t' + str(key[4]) + '\t' + conf0 + '\n')


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

    parser.add_argument('--device',
                        type=str,
                        default='0',
                        required=False,
                        help="cuda devices comma seperated")

    args = parser.parse_args()


    if args.device:
        os.environ['CUDA_DEVICE'] = args.device
        os.environ['cuda_device'] = args.device

    if args.mech_effect_mode == True:
        test_dir = pathlib.Path(args.root) / 'UnifiedData' / 'covid_anno_par' / 'mapped' / 'mech_effect' 
        serial_dir = pathlib.Path(args.root) / 'experiments' / args.data_combo / 'mapped' / 'mech_effect'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech_effect'


    if args.mech_effect_mode == False:
        test_dir = pathlib.Path(args.root) / 'UnifiedData' / 'covid_anno_par' / 'mapped' / 'mech'
        serial_dir = pathlib.Path(args.root) / 'experiments' / args.data_combo / 'mapped' / 'mech'
        pred_dir = pathlib.Path(args.root) / 'predictions' / args.data_combo / 'mapped' / 'mech'

    pred_dir.mkdir(parents=True, exist_ok=True)
    test_dir = pathlib.Path(test_dir) /'test.json'
    pred_path = pathlib.Path(pred_dir) / "pred.json"

    allennlp_command = [
            "allennlp",
            "predict",
            str(serial_dir),
            str(test_dir),
            "--predictor dygie",
            "--include-package dygie",
            "--use-dataset-reader",
            "--output-file",
            str(pred_path),
            "--cuda-device",
            args.device
    ]

    subprocess.run(" ".join(allennlp_command), shell=True, check=True)
    ds = Dataset(pred_path)
    prediction_to_tsv(ds, pathlib.Path(pred_dir) / "pred.tsv")
    