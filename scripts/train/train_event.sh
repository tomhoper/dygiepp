# USAGE: `bash train.sh [config_name]`
#
# The `config_name` is the name of one of the `jsonnet` config files in the
# `training_config` directory, for instance `scierc`. The result of training
# will be placed under `models/[config_name]`.




import argparse
import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict
from pathlib import Path
import pathlib

if __name__ == '__main__':

    allennlp_command = [
            "allentune",
            "search",
            "--experiment-name",
            "/data/aida/covid_aaai/experiments/events"
            "--num-gpus",
            "3",
            "--num-cpus",
            "3",
            "--gpus-per-trial",
            "1",
            "--cpus-per-trial",
            "1",  
            "--search-space",
            "./training_config/search_space.json",
            "--num-samples",
            "30",
            "--base-config",
            "./training_config/covid-event-biomedroberta.jsonnet",
            "--include-package",
            "dygie"
    ]
    subprocess.run(" ".join(allennlp_command), shell=True, check=True)







