import subprocess
import multiprocessing

model_dir = "/data/dwadden/proj/dygie/dygiepp-new/models"


def predict_shard(input_dict):
    shard_id = input_dict["shard_id"]
    model_name = input_dict["model_name"]
    cmd = ["allennlp", "predict",
           f"{model_dir}/{model_name}/model.tar.gz",
           f"data/shards/shard-{shard_id}.jsonl",
           "--predictor", "dygie",
           "--include-package", "dygie",
           "--use-dataset-reader",
           "--output-file", f"results/predictions/{shard_id}-{model_name}.jsonl",
           "--overrides", "{'dataset_reader' +: {'lazy': true}}",
           "--cuda-device", str(shard_id - 1),
           "--silent"]

    stdout_file = f"log/stdout-{shard_id}-{model_name}.log"
    stderr_file = f"log/stderr-{shard_id}-{model_name}.log"

    with open(stdout_file, "w", buffering=1) as f_stdout, \
            open(stderr_file, "w", buffering=1) as f_stderr:
        subprocess.run(cmd, stdout=f_stdout, stderr=f_stderr)

####################


workers = multiprocessing.Pool(4)
inputs = [{"shard_id": i + 1, "model_name": "scierc"} for i in range(4)]
workers.map(predict_shard, inputs)
