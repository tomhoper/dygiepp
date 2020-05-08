# Train DyGIE++ model on the genia data set, without coreference.
# Usage: bash scripts/train/train_genia_lightweight.sh [gpu-id]
# gpu-id can be an integer GPU ID, or -1 for CPU.

experiment_name="genia-lightweight"
data_root="./data/genia/processed-data/json-ner"
config_file="./training_config/genia_lightweight.jsonnet"
cuda_device=$1

# Train model.
ie_train_data_path=$data_root/train.json \
    ie_dev_data_path=$data_root/dev.json \
    ie_test_data_path=$data_root/test.json \
    cuda_device=$cuda_device \
    allennlp train $config_file \
    --cache-directory $data_root/cached \
    --serialization-dir ./models/$experiment_name \
    --include-package dygie
