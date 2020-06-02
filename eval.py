import argparse
import json
import os
import shutil
import subprocess
from typing import Any, Dict
import sys
# sys.path.append("../../")
# from dygie_visualize_util import Dataset


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

def eval_model_preds(gold_path, pred_path):
    golddf = pd.read_csv(gold_path, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]

    #read predictions, place in dictionary
    predf = pd.read_csv(pred_path, sep="\t",names=["id","text","arg0","arg1","rel","conf"])
    

    prediction_dict = {}
    prediction_dict["model preds"] = predf[["id","arg0","arg1"]]
    
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

    parser.add_argument('--test_dir',
                        type=str,
                        default='UnifiedData/covid_anno_par/mapped/mech_effect/',
                        help='path to save the predictions',
                        required=False)

    parser.add_argument('--serialdir',
                        type=str,
                        help='path to serialize',
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
    prediction_to_tsv(ds, args.test_dir + "pred.tsv")
    # subprocess.call(["activate", "covid_eval"])
    # import pdb; pdb.set_trace()
    
    # from allennlp.common.params import Params
    # from eval_utils import *
    # eval_model_preds("gold_par.tsv", args.test_dir + "pred.tsv")
