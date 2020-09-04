# Evaluate the performance of both models on scierc, to see how they compare.

dygie_dir=/data/dwadden/proj/dygie/dygiepp-new
model_dir=$dygie_dir/models
data_dir=$dygie_dir/data/scierc/normalized_data/json
out_dir=results/scierc-performance

for model_name in scierc genia-scierc
do
    allennlp evaluate $model_dir/$model_name/model.tar.gz \
    $data_dir/test.json \
    --include-package dygie \
    --output-file $out_dir/$model_name.jsonl \
    --cuda-device 0
done
