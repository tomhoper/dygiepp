import os
import argparse
import pathlib
import shutil
import subprocess
from pathlib import Path
import pandas as pd




if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)

    args = parser.parse_args()
    s_dir = pathlib.Path(args.root) / 'stats'
    exp_name_list = os.listdir(str(s_dir))
    print(exp_name_list)
    # import pdb;pdb.set_trace()
    df_list = []
    for name in exp_name_list:
      if not os.path.isdir(str(s_dir) + '/' + name):
        continue
      mech_effect_exps_path = pathlib.Path(s_dir) / name / 'mapped'
      mech_effect_exps = os.listdir(mech_effect_exps_path)
      print(mech_effect_exps)
      print(name)
      # import pdb; pdb.set_trace()
      for n in mech_effect_exps:
        print(n)
        if "mech" == n:
            stat_dir = pathlib.Path(args.root) / 'stats' / name / 'mapped' / 'mech' / 'stats.tsv'
            
        elif "mech_effect" == n:
            stat_dir = pathlib.Path(args.root) / 'stats' / name / 'mapped' / 'mech_effect' / 'stats.tsv'

        df = pd.read_csv(stat_dir, sep="\t",encoding="utf-8")
        df_list.append(df)

    result = pd.concat(df_list)
    result = result.drop_duplicates()
    tota_stats_path = s_dir / 'complete_stats.tsv'
    result.to_csv(tota_stats_path,header=True,index=False, sep="\t")

