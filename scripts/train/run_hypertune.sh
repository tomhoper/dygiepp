python dygie/data/merge_corpus.py --root $1 --dataset_list $2
if [ $4 = "mech" ]; then
  if [$7 == "covid_dev"]; then
    python scripts/train/train_allentune.py --root $1 --data_combo $2  --gpu_count $5 --cpu_count $6  --num_samples $3 --covid_only_dev --dev_path $8
  else
    python scripts/train/train_allentune.py --root $1 --data_combo $2  --gpu_count $5 --cpu_count $6  --num_samples $3
  fi
else
  if [$7 == "covid_dev"]; then
   python scripts/train/train_allentune.py --root $1 --data_combo $2 --mech_effect_mode --gpu_count $5 --cpu_count $6 --num_samples $3 --covid_only_dev --dev_path $8
  else
   python scripts/train/train_allentune.py --root $1 --data_combo $2 --mech_effect_mode --gpu_count $5 --cpu_count $6 --num_samples $3
  fi
fi
