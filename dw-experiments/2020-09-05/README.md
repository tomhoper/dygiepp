This is an exact copy of `2020-09-04`. The only change is the way the data are split; I use Aida's split instead of just doing one randomly myself. The input data are from `allgood:/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect`. I put them in `data/raw/mech_effect`. I changed the extensions from `json` to `jsonl` to match what I have in the rest of the scripts.

The numbers on the scripts are also decremented by 1, since we no longer need the first script to process the event data.

## Steps to reproduce

These steps should work. For a description of what's going on, see the "Scripts" section below for details of inputs and outputs.

- Copy the data from `allgood:/data/aida/covid_aaai/UnifiedData/events_covid/mapped/mech_effect` to `data/raw/mech_effect`.
- Run `python script/01_collate.py`
- Run `python script/02_check_folds.py` to make sure the train, dev, and test folds are disjoint.
- Run `bash script/train.sh covid-event-biomedroberta` and `bash script/train.sh covid-event-pubmedbert`. This will train the event models.
- Run `bash script/evaluate.sh covid-event-biomedroberta` and `bash script/evaluate.sh covid-event-pubmedbert` to evaluate using old "ACE-style" metrics.
- Run `bash script/predict.sh covid-event-biomedroberta` and `bash script/predict.sh covid-event-pubmedbert` to make predictions.
- Then, run the remaining numbered Python scripts in order, from `03_collect_results.py` to `6_metrics_exact_match.py`. 


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


## Scripts

Details of what's going on in the scripts.

### Ordered

- `01_collate.py`: Split into train / dev / test and collate.
- `02_check_folds.py`: The results are so good, I wanted to double-check that the folds are disjoint.
- `03_collect_results.py`: Make a table.
  - Outputs: `results/summary.tsv`, `results/summary.md` (shown above).
- `05_double_check.py`: Double-check the metrics I report. There are a few wrinkles here:
  - 4or ACE, a token can only trigger a single event. This isn't the case for our data.
  - For ACE eveluation, an argument is correct if the span, event type, and argument type are correct. Since there's only one event type, this is kind of easy as an evaluation for the COVID data.
  - For ACE, there can be multiple arguments of the same type; for us, a given trigger always has two arguments, with a single argument of each type.
  - Based on these differences, it makes sense to further "decode" the COVID event predictions to match the COVID data format. I'll do that decoding.
- `05_decode_predictions.py`: Decode into COVID event format.
  - Outputs: `results/predictions/events-pubmedbert/decoded`.
- `06_convert_to_tsv.py`: Convert gold data and predictions to `.tsv`. The output goes to `results/predictions/covid-event-pubmedbert/tsv` Each line has:
  - Document ID.
  - Sentence.
  - arg0
  - trig
  - arg1
  - (arg0, trig, arg1)_logit (predicted only).
  - (arg0, trig, arg1)_softmax (predictions only.)
- `08_metrics_exact_match.py`: Compute exact match metrics. Model only gets credit for an event if it correctly predicts trig, arg0, and arg1 exactly.
  - Outputs: `results/summary-exact-match`


### Library-ish

- `train.sh`: Run training.
  - Outputs: `models`
- `evaluate.sh`: Run test set evaluation.
  - Outputs: `results/metrics`
- `predict.sh`: Make predictions using PubMedBERT, which does better.
  - Outputs: `results/predictions/covid-event-pubmedbert/collated`
- `decode.py`: Decode predictions so that they match the format for our data rather than the ACE data.

## Annotation notes from Tom

- Ignore relations between two `ENTITY`'s and only look at relations between a `TRIGGER` and an `ENTITY`.
- Here's the way to generate SciERC events from these annotations:
  - for every TRIGGER entity t,
    - for every  TRIGGER_ARG0 relation outgoing from t to entity e0,
      - for every  TRIGGER_ARG1 relation outgoing from t to entity e1 ,
        - create “event” e <- [e0, t, e1]
