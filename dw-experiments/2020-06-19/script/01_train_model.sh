experiment_name="covid_anno_par_mech_effect"

model_dir=$PWD/models
dygie_dir=../..

cd $dygie_dir
data_root="./data/UnifiedData/covid_anno_par/mapped/mech_effect"
config_file="./training_config/scierc_lightweight.jsonnet"
cuda_device=0

# Train model.
ie_train_data_path=$data_root/train.json \
    ie_dev_data_path=$data_root/dev.json \
    ie_test_data_path=$data_root/test.json \
    cuda_device="$cuda_device" \
    allennlp train $config_file \
    --cache-directory $data_root/cached \
    --serialization-dir $model_dir/$experiment_name \
    --include-package dygie
