"""
Evaluate model performance.
"""

import subprocess
import itertools

models = ["no-spike", "spike-0", "spike-2", "spike-4"]
folds = ["dev", "test"]

for model, fold in itertools.product(models, folds):
    cmd = ["allennlp", "evaluate",
           f"models/{model}",
           f"data/processed/{fold}.json",
           "--include-package", "dygie",
           "--cuda-device", "0",
           "--output-file", f"results/metrics/{model}-{fold}.json"]
    subprocess.run(cmd)
