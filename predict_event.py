# Predict, then uncollate
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
from dygie.data.dataset_readers import document
import pandas as pd
from decode import decode

def stringify(xs):
    return " ".join(xs)

def format_predicted_events(sent, doc_key=""):
    res = []
    for event in sent.predicted_events:
        if len(event.arguments) < 2:
          continue
        arg0 = event.arguments[0]
        arg1 = event.arguments[1]

        entry = {"doc_key": sent.metadata["_orig_doc_key"],
                 "sentence": stringify(sent.text),
                 "arg0": stringify(arg0.span.text),
                 "trigger": event.trigger.token.text,
                 "arg1": stringify(arg1.span.text),
                 "arg0_logit": arg0.raw_score,
                 "trigger_logit": event.trigger.raw_score,
                 "arg1_logit": arg1.raw_score,
                 "arg0_softmax": arg0.softmax_score,
                 "trigger_softmax": event.trigger.softmax_score,
                 "arg1_softmax": arg1.softmax_score}
        res.append(entry)
    return res


def format_dataset(dataset):
    predicted_events = []

    for doc in dataset:

        # import pdb; pdb.set_trace()
        for sent in doc:
          
            predicted = format_predicted_events(sent)
            predicted_events.extend(predicted)

    predicted_events = pd.DataFrame(predicted_events)

    return predicted_events

def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('--root',
                        type=Path,
                        help='/data/aida/covid_aaai/',
                        required=True)

    parser.add_argument('--test_data',
                        action='store_true')
    
    parser.add_argument('--test_index',
                        type=int,
                        default=0)

    args = parser.parse_args()

    # test_dir = pathlib.Path(args.root) / 'UnifiedData' / 'covid_anno_par_madeline_sentences_matchcd' / 'mapped' / 'mech_effect' 
    serial_dir = pathlib.Path(args.root) / 'experiments' / "events" 
    if args.test_data:
      collated_pred_dir = pathlib.Path(args.root) / 'predictions' / "events" / 'mapped_collated' / 'mech_effect'
      pred_dir = pathlib.Path(args.root) / 'predictions' / "events" / 'mapped' / 'mech_effect'
    else:
      collated_pred_dir = pathlib.Path(args.root) / 'predictions_dev' / "events" / 'mapped_collated' / 'mech_effect'
      pred_dir = pathlib.Path(args.root) / 'predictions_dev' / "events" / 'mapped' / 'mech_effect'
    # test_dir = "/home/aida/covid_clean/dygiepp/data/processed/split"
    test_dir = "/home/aida/covid_clean/dygiepp/data/processed/collated/"
    if args.test_data:
      test_dir = pathlib.Path(test_dir) /'test.json'
    else:
      test_dir = pathlib.Path(test_dir) /'dev.json'
   

    for file in os.listdir(str(serial_dir)):
      if file == "run_24_2020-09-06_18-11-23_t9lt_5l" or file == "run_24_2020-09-06_17-58-095u168rv5" or file == "run_24_2020-09-06_18-10-15_y8crruz":
          continue
      # if file != "run_18_2020-09-06_21-10-48w170bpge":
        # continue
      trail_strat_str = "run_"
      if args.test_data:
        trail_strat_str = trail_strat_str + str(args.test_index)

      if file.startswith(trail_strat_str):
        run_serial_dir = serial_dir / file / "trial"
        run_pred_dir = collated_pred_dir / file 
        uncollate_pred_dir = pred_dir / file
        run_pred_dir.mkdir(parents=True, exist_ok=True)
        uncollate_pred_dir.mkdir(parents=True, exist_ok=True)
        
        
        # pred_path = pathlib.Path(run_pred_dir) / "pred.json"
        uncollated_pred_path = pathlib.Path(uncollate_pred_dir) / "pred.json"
        uncollated_pred_path_decode = pathlib.Path(uncollate_pred_dir) / "decode.json"
        uncollated_pred_path_tsv = pathlib.Path(uncollate_pred_dir) / "pred.tsv"


        allennlp_command = [
                  "allennlp",
                  "predict",
                  str(run_serial_dir),
                  str(test_dir),
                  "--predictor dygie",
                  "--include-package dygie",
                  "--use-dataset-reader",
                  "--output-file",
                  str(uncollated_pred_path),
                  "--cuda-device",
                  "0"
          ]
        # print(" ".join(allennlp_command))
        try:
          subprocess.run(" ".join(allennlp_command), shell=True, check=True)
          
        # try:
        # cmd = ["python", "scripts/data/shared/uncollate.py",
        #        str(uncollate_pred_dir),
        #        str(uncollate_pred_dir),
        #        "--file_extension=json",
        #        "--train_name=skip",
        #        "--test_name=skip",
        #        "--dev_name=pred"]
        # print(' '.join(cmd))
        # subprocess.run(cmd)
          in_data = load_jsonl(str(uncollated_pred_path))
          out_data = decode(in_data)
          save_jsonl(out_data, str(uncollated_pred_path_decode))
          dataset = document.Dataset.from_jsonl(str(uncollated_pred_path_decode))
        # except:
        #   continue
          print(len(dataset))
          pred = format_dataset(dataset)
          pred.to_csv(str(uncollated_pred_path_tsv), sep="\t", float_format="%0.4f", index=False)
      # prediction_to_tsv(ds, pathlib.Path(uncollate_pred_dir) / "pred.tsv")

        except:
           os.rmdir(str(uncollate_pred_dir))
           continue





# uncollate=scripts/data/shared/uncollate.py

# # Only do pubmebert, since it gets slightly better results.
# config_name="covid-event-pubmedbert"

# pred_dir=results/predictions/$config_name
# collated_dir=$pred_dir/collated
# uncollated_dir=$pred_dir/uncollated


# mkdir -p $collated_dir
# mkdir -p $uncollated_dir


    
