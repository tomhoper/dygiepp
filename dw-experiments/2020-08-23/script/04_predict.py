"""
Make dev and test set predictions for all models.
"""

import os
import itertools
import subprocess


models = ["no-spike", "spike-0", "spike-2", "spike-4"]
folds = ["dev", "test"]

# Make predictions.
for model, fold in itertools.product(models, folds):
    os.makedirs(f"results/predictions/collated/{model}", exist_ok=True)
    cmd = ["allennlp", "predict",
           f"models/{model}",
           f"data/processed/{fold}.json",
           "--predictor", "dygie",
           "--include-package", "dygie",
           "--use-dataset-reader",
           "--output-file", f"results/predictions/collated/{model}/{fold}.json",
           "--cuda-device", "0",
           "--silent"]
    subprocess.run(cmd)


# Un-collate the results to match the input order.
for model in models:
    in_dir = f"results/predictions/collated/{model}"
    out_dir = f"results/predictions/final/{model}"
    os.makedirs(out_dir, exist_ok=True)
    cmd = ["python", "../../scripts/data/shared/uncollate.py",
           in_dir,
           out_dir,
           "--order_like=data/cleanup/covid",
           "--file_extension=json",
           "--train_name=skip"]
    subprocess.run(cmd)
