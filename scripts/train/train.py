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
                        default="./training_config/scierc.jsonnet",
                        help='training config',
                        required=False)
 
    parser.add_argument('--data_combo',
                        type=Path,
                        help='root dataset folder, contains mapped/mech, mapped/mech_effect and then train,dev,test',
                        required=True)

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)

    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--single_source',
                        action='store_true')

    parser.add_argument('--device',
                        type=str,
                        default='1,2,3',
                        required=False,
                        help="cuda devices comma seperated")

    args = parser.parse_args()
    if args.single_source:
        data_root_dir = "UnifiedData"
    else:
        data_root_dir = "combo"
    if args.mech_effect_mode == True:
        data_root = pathlib.Path(args.root) / data_root_dir / args.data_combo / 'mapped' / 'mech_effect'
        serial_dir = pathlib.Path(args.root) / 'experiments' / args.data_combo / 'mapped' / 'mech_effect'
    if args.mech_effect_mode == False:
        data_root = pathlib.Path(args.root) / data_root_dir / args.data_combo / 'mapped' / 'mech'
        serial_dir = pathlib.Path(args.root) / 'experiments' / args.data_combo / 'mapped' / 'mech'


    config_file = args.config
    experiment_name = args.data_combo
    os.environ['experiment_name'] = str(experiment_name)
    
    cachedir = data_root/"cached"
    print(serial_dir)
    ie_train_data_path = data_root/"train.json"
    ie_dev_data_path = data_root/"dev.json"
    ie_test_data_path = data_root/"test.json"
    os.environ['ie_train_data_path'] = str(ie_train_data_path)
    os.environ['ie_dev_data_path'] = str(ie_dev_data_path)
    os.environ['ie_test_data_path'] = str(ie_test_data_path)

    if args.device:
        os.environ['CUDA_DEVICE'] = args.device
        os.environ['cuda_device'] = args.device

    allennlp_command = [
            "allennlp",
            "train",
            config_file,
            "--serialization-dir",
            str(serial_dir),
            "--include-package",
            "dygie"
    ]
    
   
    subprocess.run(" ".join(allennlp_command), shell=True, check=True)

