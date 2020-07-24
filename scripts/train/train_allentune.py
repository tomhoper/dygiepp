import argparse
import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict
from pathlib import Path
import pathlib

"""
Usage
python scripts/train/train.py --data_combo chemprot --root ../coviddata/ --device 0,1
python scripts/train/train.py --data_combo chemprot --root  ../coviddata/ --mech_effect_mode --device 2


"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--config',
                        type=str,
                        default="./training_config/scierc_working_allentune.jsonnet",
                        help='training config',
                        required=False)

    parser.add_argument('--search_space',
                        type=str,
                        default="./training_config/search_space.json",
                        help='training config',
                        required=False)
 
    parser.add_argument('--data_combo',
                        type=str,
                        help='root dataset folder, contains mapped/mech, mapped/mech_effect and then train,dev,test',
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--gpu_count',
                        type=int,
                        default=3,
                        required=False,
                        help="cuda devices comma seperated")

    parser.add_argument('--cpu_count',
                        type=int,
                        default=32,
                        required=False,
                        help="cuda devices comma seperated")
    
    parser.add_argument('--num_samples',
                        type=int,
                        default=30,
                        required=False,
                        help="")



    args = parser.parse_args()
    if ',' not in args.data_combo:
        data_root_dir = "UnifiedData"
    else:
        data_root_dir = "combo"
    
    experiment_name = '_'.join(args.data_combo.split(','))
    if args.mech_effect_mode == True:
        data_root = pathlib.Path(args.root) / data_root_dir / experiment_name / 'mapped' / 'mech_effect'
        serial_dir = pathlib.Path(args.root) / 'experiments' / experiment_name / 'mapped' / 'mech_effect'
    if args.mech_effect_mode == False:
        data_root = pathlib.Path(args.root) / data_root_dir / experiment_name / 'mapped' / 'mech'
        serial_dir = pathlib.Path(args.root) / 'experiments' / experiment_name / 'mapped' / 'mech'


    gpu_count = args.gpu_count
    num_samples = args.num_samples
    config_file = args.config
    search_space = args.search_space
    
    os.environ['experiment_name'] = str(experiment_name)
    
    cachedir = data_root/"cached"
    print(serial_dir)
    ie_train_data_path = data_root/"train.json"
    ie_dev_data_path = data_root/"dev.json"
    ie_test_data_path = data_root/"test.json"
    os.environ['ie_train_data_path'] = str(ie_train_data_path)
    os.environ['ie_dev_data_path'] = str(ie_dev_data_path)
    os.environ['ie_test_data_path'] = str(ie_test_data_path)

    if args.gpu_count > 0:
        os.environ['CUDA_DEVICE'] = [i for i in range(args.gpu_count)]
        os.environ['cuda_device'] = [i for i in range(args.gpu_count)]
    
    allennlp_command = [
            "allentune",
            "search",
            "--experiment-name",
            str(serial_dir),
            "--num-gpus",
            str(gpu_count),
            "--gpus-per-trial",
            "1",
            "num-cpus",
            "1",       
            "--search-space",
            search_space,
            "--num-samples",
            str(num_samples),
            "--base-config",
            config_file            ,
            "--include-package",
            "dygie"
    ]
    # import pdb; pdb.set_trace()
    subprocess.run(" ".join(allennlp_command), shell=True, check=True)







