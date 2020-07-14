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
        try:
          df = pd.read_csv(stat_dir, sep="\t",encoding="utf-8")
          df_list.append(df)
        except:
            pass
    
    # nocollapsed = df_list[df_list["collapsed"] == True]



    result = pd.concat(df_list)
    result = result.drop_duplicates()
    tota_stats_path = s_dir / 'complete_stats.tsv'
    result.to_csv(tota_stats_path,header=True,index=False, sep="\t")
    # 

    collapsed = result.loc[result["collapse"] == True]

    collapsed_substr = collapsed.loc[collapsed["match_mettric"] == "substring"]
    collapsed_jaccard = collapsed.loc[collapsed["match_mettric"] == "jaccard"]

    # import pdb; pdb.set_trace()
    collapsed_jaccard3 = collapsed_jaccard.loc[collapsed_jaccard["threshold"] == 0.3]
    collapsed_jaccard4 = collapsed_jaccard.loc[collapsed_jaccard["threshold"] == 0.4]
    collapsed_jaccard5 = collapsed_jaccard.loc[collapsed_jaccard["threshold"] == 0.5]

    non_collapsed = result[result["collapse"] == False]

    non_collapsed_substr = non_collapsed.loc[non_collapsed["match_mettric"] == "substring"]
    non_collapsed_jaccard = non_collapsed.loc[non_collapsed["match_mettric"] == "jaccard"]


    non_collapsed_jaccard3 = non_collapsed_jaccard.loc[non_collapsed_jaccard["threshold"] == 0.3]
    non_collapsed_jaccard4 = non_collapsed_jaccard.loc[non_collapsed_jaccard["threshold"] == 0.4]
    non_collapsed_jaccard5 = non_collapsed_jaccard.loc[non_collapsed_jaccard["threshold"] == 0.5]

    collapsed_substr_dir = s_dir / 'collapsed_substr.tsv'
    collapsed_substr.to_csv(collapsed_substr_dir,header=True,index=False, sep="\t")
    collapsed_jaccard3_dir = s_dir / 'collapsed_jaccard3.tsv'
    collapsed_jaccard3.to_csv(collapsed_jaccard3_dir,header=True,index=False, sep="\t")
    collapsed_jaccard4_dir = s_dir / 'collapsed_jaccard4.tsv'
    collapsed_jaccard4.to_csv(collapsed_jaccard4_dir,header=True,index=False, sep="\t")
    collapsed_jaccard5_dir = s_dir / 'collapsed_jaccard5.tsv'
    collapsed_jaccard5.to_csv(collapsed_jaccard5_dir,header=True,index=False, sep="\t")

    non_collapsed_substr_dir = s_dir / 'non_collapsed_substr.tsv'
    non_collapsed_substr.to_csv(non_collapsed_substr_dir,header=True,index=False, sep="\t")
    non_collapsed_jaccard3_dir = s_dir / 'non_collapsed_jaccard3.tsv'
    non_collapsed_jaccard3.to_csv(non_collapsed_jaccard3_dir,header=True,index=False, sep="\t")
    non_collapsed_jaccard4_dir = s_dir / 'non_collapsed_jaccard4.tsv'
    non_collapsed_jaccard4.to_csv(non_collapsed_jaccard4_dir,header=True,index=False, sep="\t")
    non_collapsed_jaccard5_dir = s_dir / 'non_collapsed_jaccard5.tsv'
    non_collapsed_jaccard5.to_csv(non_collapsed_jaccard5_dir,header=True,index=False, sep="\t")

    





















