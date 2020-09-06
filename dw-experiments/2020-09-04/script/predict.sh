# Predict, then uncollate

uncollate=../../scripts/data/shared/uncollate.py

# Only do pubmebert, since it gets slightly better results.
config_name="covid-event-pubmedbert"

pred_dir=results/predictions/$config_name
collated_dir=$pred_dir/collated
uncollated_dir=$pred_dir/uncollated

mkdir -p $collated_dir
mkdir -p $uncollated_dir

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
