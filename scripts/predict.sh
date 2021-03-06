# Predict, then uncollate

uncollate=scripts/data/shared/uncollate.py

# Only do pubmebert, since it gets slightly better results.
config_name="covid-event-pubmedbert"

pred_dir=results/predictions/$config_name
collated_dir=$pred_dir/collated
uncollated_dir=$pred_dir/uncollated

mkdir -p $collated_dir
mkdir -p $uncollated_dir
for file in os.listdir(str(serial_dir)):
      trail_strat_str = "run_"
      if args.test_data:
        trail_strat_str = trail_strat_str + str(args.test_index)
      
      if file.startswith(trail_strat_str):

for fold in train dev test
do
    allennlp predict \
        models/$config_name/model.tar.gz \
        data/processed/collated/$fold.jsonl \
        --predictor dygie \
        --include-package dygie \
        --use-dataset-reader \
        --cuda-device 0 \
        --output-file $collated_dir/$fold.jsonl \
        --silent
done
