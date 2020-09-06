"""
Collate Aida's data.
"""

import subprocess


# Collate the data
collate_path = "../../scripts/data/shared/collate.py"

cmd = ["python", collate_path,
       "data/raw/mech_effect",
       "data/processed/collated"]
subprocess.run(cmd)
