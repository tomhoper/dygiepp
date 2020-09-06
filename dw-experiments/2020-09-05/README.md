This is an exact copy of `2020-09-04`. The only change is the way the data are split; I use Aida's split instead of just doing one randomly myself. The input data are from `/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect`. I put them in `data/raw/mech_effect`. I changed the extensions from `json` to `jsonl` to match what I have in the rest of the scripts.

The numbers on the scripts are also decremented by 1, since we no longer need the first script to process the event data.



## Results (Exact match)

|       |   precision |   recall |     f1 |
|-------|-------------|----------|--------|
| train |      0.9337 |   0.8820 | 0.9071 |
| dev   |      0.3498 |   0.2545 | 0.2946 |
| test  |      0.2880 |   0.2097 | 0.2427 |


## Results (ACE-style evaluation)

**NOTE**: This is an overestimate of performance.

|                      |   biomedroberta |   pubmedbert |
|----------------------|-----------------|--------------|
| trig_class_precision |          0.6442 |       0.6447 |
| trig_class_recall    |          0.6700 |       0.6833 |
| trig_class_f1        |          0.6569 |       0.6634 |
| arg_class_precision  |          0.5504 |       0.5795 |
| arg_class_recall     |          0.5034 |       0.5062 |
| arg_class_f1         |          0.5259 |       0.5404 |
