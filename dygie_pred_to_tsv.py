import argparse
import json
from typing import Any, Dict
import sys
from dygie_visualize_util import Dataset
import pathlib
from pathlib import Path

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
    if key[4] == "USED-FOR":
      conf0 = str(doc_info[key])
      output_file.write(key[0] + '\t' + key[1] + '\t' + key[2] + '\t' + key[3] + '\tMECHANISM\t' + conf0 + '\n')
    elif key[4] in ['PART-OF','HYPONYM-OF','CONJUNCTION','FEATURE-OF','COMPARE','EVALUATE-FOR']:
      continue
    # conf0 = str(doc_info[key])
    # output_file.write(key[0] + '\t' + key[1] + '\t' + key[2] + '\t' + key[3] + '\t' + str(key[4]) + '\t' + conf0 + '\n')



if __name__ == '__main__':

    parser = argparse.ArgumentParser() 

    parser.add_argument('--data_combo',
                        type=str,
                        help='',
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')


    args = parser.parse_args()
    if args.mech_effect_mode == True:
        pred_dir = pathlib.Path(args.root)  / args.data_combo / 'mapped' / 'mech_effect'


    if args.mech_effect_mode == False:
        pred_dir = pathlib.Path(args.root) / args.data_combo / 'mapped' / 'mech'

    pred_dir.mkdir(parents=True, exist_ok=True)
    pred_path = pathlib.Path(pred_dir) / "pred.json"

    ds = Dataset(pred_path)
    prediction_to_tsv(ds, pathlib.Path(pred_dir) / "pred.tsv")
