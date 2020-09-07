This is an exact copy of `2020-09-04`. The only change is the way the data are split; I use Aida's split instead of just doing one randomly myself. The input data are from `allgood:/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect`. I put them in `data/raw/mech_effect`. I changed the extensions from `json` to `jsonl` to match what I have in the rest of the scripts.

The numbers on the scripts are also decremented by 1, since we no longer need the first script to process the event data.

## Steps to reproduce

These steps should work. For a description of what's going on, see the README from [2020-09-04](https://github.com/tomhoper/dygiepp/blob/master/dw-experiments/2020-09-04/README.md); it provides a description of the inputs and outputs. The only difference between that experiment and this one is the split used for the event data.

- Copy the data from `allgood:/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect` to `data/raw/mech_effect`.
- Run `python script/01_collate.py`
- Run `python script/02_check_folds.py` to make sure the train, dev, and test folds are disjoint.
- Run `bash script/train.sh covid-event-biomedroberta` and `bash script/train.sh covid-event-pubmedbert`. This will train the event models.
- Run `bash script/evaluate.sh covid-event-biomedroberta` and `bash script/evaluate.sh covid-event-pubmedbert` to evaluate using old "ACE-style" metrics.
- Run `bash script/predict.sh covid-event-biomedroberta` and `bash script/predict.sh covid-event-pubmedbert` to make predictions.
- Then, run the remaining numbered Python scripts in order, from `03_collect_results.py` to `07_metrics_exact_match.py`. 


## Results (Exact match)

|       |   precision |   recall |     f1 |
|-------|-------------|----------|--------|
| train |      0.8223 |   0.8465 | 0.8342 |
| dev   |      0.2364 |   0.2319 | 0.2342 |
| test  |      0.2800 |   0.2314 | 0.2534 |


## Results (ACE-style evaluation)

**NOTE**: This is an overestimate of performance.


|                      |   biomedroberta |   pubmedbert |
|----------------------|-----------------|--------------|
| trig_class_precision |          0.6279 |       0.6265 |
| trig_class_recall    |          0.7132 |       0.7660 |
| trig_class_f1        |          0.6678 |       0.6893 |
| arg_class_precision  |          0.6142 |       0.5856 |
| arg_class_recall     |          0.4304 |       0.5968 |
| arg_class_f1         |          0.5061 |       0.5911 |
