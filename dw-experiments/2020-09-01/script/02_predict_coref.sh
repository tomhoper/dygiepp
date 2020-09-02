# Make coref predictions.

model_dir=/data/dwadden/proj/dygie/dygiepp-new/models

# Make predictions with models train on scierc alone, and scierc + genia.
for model_name in scierc genia-scierc
do
    allennlp predict $model_dir/$model_name/model.tar.gz \
        data/merged.jsonl \
        --predictor dygie \
        --include-package dygie \
        --use-dataset-reader \
        --output-file results/predictions/$model_name.jsonl \
        --cuda-device 0 \
        --silent
done
