experiment_name="chemprot_mech_effect"

experiment_dir=$PWD
model_dir=$PWD/models
dygie_dir=../..

cd $dygie_dir
data_file="./data/UnifiedData/covid_anno_par/mapped/mech_effect/test.json"

allennlp predict $model_dir/$experiment_name/model.tar.gz \
    $data_file \
    --predictor dygie \
    --include-package dygie \
    --use-dataset-reader \
    --output-file $experiment_dir/results/covid_anno_par_mech_effect_test.json \
    --cuda-device 0
