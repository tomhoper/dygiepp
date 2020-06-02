import argparse
import json
import os
import shutil
import subprocess
from typing import Any, Dict
import sys
from dygie_visualize_util import Dataset



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

    parser.add_argument('--pred_path',
                        type=str,
                        help='path to save the predictions',
                        required=True)

    parser.add_argument('--test_dir',
                        type=str,
                        default='UnifiedData/covid_anno_par/mapped/mech_effect/',
                        help='path for gold test',
                        required=False)

    parser.add_argument('--serialdir',
                        type=str,
                        help='path to serialized model',
                        required=True)

    parser.add_argument('--device',
                        type=str,
                        default='0',
                        required=False,
                        help="cuda devices comma seperated")

    args = parser.parse_args()


    if args.device:
        os.environ['CUDA_DEVICE'] = args.device
        os.environ['cuda_device'] = args.device

    allennlp_command = [
            "allennlp",
            "predict",
            args.serialdir,
            args.test_dir + 'test.json',
            "--predictor dygie",
            "--include-package dygie",
            "--use-dataset-reader",
            "--output-file",
            args.pred_path,
            "--cuda-device",
            args.device
    ]
    subprocess.run(" ".join(allennlp_command), shell=True, check=True)
    ds = Dataset(args.pred_path)
    prediction_to_tsv(ds, args.pred_path + "pred.tsv")
    
