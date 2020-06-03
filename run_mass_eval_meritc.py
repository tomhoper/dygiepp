import os
import argparse
import pathlib
import shutil
import subprocess
from pathlib import Path


if __name__ == '__main__':

    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)

    args = parser.parse_args()
    exp_dir = pathlib.Path(args.root) / 'experiments'
    exp_name_list = os.listdir(str(exp_dir))
    
    for name in exp_name_list:
      mech_effect_exps_path = pathlib.Path(exp_dir) / name / 'mapped'
      mech_effect_exps = os.listdir(mech_effect_exps_path)
      
      print(name)
      if "mech" in mech_effect_exps:
        eval_command = [
                "python",
                "eval_metric.py",
                "--root",
                str(args.root),
                "--data_combo",
                name
        ]
        subprocess.run(" ".join(eval_command), shell=True, check=True)

      if "mech_effect" in mech_effect_exps:
        eval_command = [
                "python",
                "eval_metric.py",
                "--root",
                str(args.root),
                "--data_combo",
                str(name),
                "--mech_effect_mode"
        ]
        subprocess.run(" ".join(eval_command), shell=True, check=True)

