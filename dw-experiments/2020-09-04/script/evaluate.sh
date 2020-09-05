config_name=$1

allennlp evaluate \
    models/$config_name/model.tar.gz \
    data/processed/collated/test.jsonl \
    --cuda-device 0 \
    --include-package dygie \
    --output-file results/metrics/$config_name.json
