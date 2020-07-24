python dygie/data/merge_corpus.py --root $1 --dataset_list $2
if [ $4 = "mech" ]; then
  echo "mech only mode"
  python scripts/train/train_allentune.py --root $1 --data_combo $2 --mech_effect_mode --gpu_count $4 --device 0,1,2,3 --num_samples $3
else
  echo "effect and mech mode"
  python scripts/train/train_allentune.py --root $1 --data_combo $2 --mech_effect_mode --gpu_count $4 --cpu_count $5 --device 0,1,2,3 --num_samples $3
fi
