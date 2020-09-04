# Make coref predictions on SciERC.

dygie_dir=/data/dwadden/proj/dygie/dygiepp-new
model_dir=$dygie_dir/models

# Make predictions with models train on scierc alone, and scierc + genia.
for model_name in scierc genia-scierc
do
    allennlp predict $model_dir/$model_name/model.tar.gz \
        $dygie_dir/data/scierc/normalized_data/json/test.json \
        --predictor dygie \
        --include-package dygie \
        --use-dataset-reader \
        --output-file results/predictions-scierc/$model_name.jsonl \
        --cuda-device 1 \
        --silent
done
