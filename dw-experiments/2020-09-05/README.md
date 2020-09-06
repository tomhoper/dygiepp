This is an exact copy of `2020-09-04`. The only change is the way the data are split; I use Aida's split instead of just doing one randomly myself. The input data are from `allgood:/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect`. I put them in `data/raw/mech_effect`. I changed the extensions from `json` to `jsonl` to match what I have in the rest of the scripts.

The numbers on the scripts are also decremented by 1, since we no longer need the first script to process the event data.



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
