import argparse
import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict
from pathlib import Path
from allennlp.common.params import Params

if __name__ == '__main__':

    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--config',
                        type=str,
                        default="./training_config/scierc_working_example.jsonnet",
                        help='training config',
                        required=False)
 
    parser.add_argument('--dataroot',
                        type=Path,
                        help='root dataset folder, contains train/dev/test',
                        required=True)

    parser.add_argument('--device',
                        type=str,
                        default='0,1,2,3',
                        required=False,
                        help="cuda devices comma seperated")

    args = parser.parse_args()
    data_root = Path(args.dataroot)

    config_file= args.config
    experiment_name = data_root
    os.environ['experiment_name'] = str(data_root)
    
    cachedir = data_root/"cached"
    serial_dir = "./models" / data_root
    
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
            "--cache-directory",
            cachedir.name,
            "--serialization-dir",
            serial_dir.name,
            "--include-package",
            "dygie"
    ]
    
   
    subprocess.run(" ".join(allennlp_command), shell=True, check=True)

