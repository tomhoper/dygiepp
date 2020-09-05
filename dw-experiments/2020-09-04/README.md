Convert Tom's event annotations to DyGIE format and train model on them.


## Experiment description

- Preprocess Tom's event annotations as described in [annotation notes from Tom](#annotation-notes-from-tom)
- Split into train, dev, test.
- Train event extraction model (using BioMedRoberta and PubMedBert).
- Evaluate results.


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


## Scripts

### Ordered

- `01_convert.py`: Convert to our format.
  - Inputs: The event annotations are copied from `allgood:/home/aida/covid_clean/dygiepp/bio_annotations/tom_event.jsonl`. I put it in `data/raw`.
  - Notes: As per Tom's message,
  - Outputs: `data/processed/events.jsonl`
- `02_split_and_collate.py`: Split into train / dev / test and collate.
  - Inputs: `data/processed/events.jsonl`
- `03_check_folds.py`: The results are so good, I wanted to double-check that the folds are disjoint.
- `04_collect_results.py`: Make a table.
  - Outputs: `results/summary.tsv`, `results/summary.md` (shown above).
- `05_double_check.py`: Double-check the metrics I report. There are a few wrinkles here:
  - For ACE, a token can only trigger a single event. This isn't the case for our data.
  - For ACE eveluation, an argument is correct if the span, event type, and argument type are correct. Since there's only one event type, this is kind of easy as an evaluation for the COVID data.
  - For ACE, there can be multiple arguments of the same type; for us, a given trigger always has two arguments, with a single argument of each type.
  - Based on these differences, it makes sense to further "decode" the COVID event predictions to match the COVID data format. I'll do that decoding.
- `06_decode_predictions.py`: Decode into COVID event format.
  - Outputs: `results/predictions/events-pubmedbert/decoded`.
- `07_convert_to_tsv.py`: Convert gold data and predictions to `.tsv`. The output goes to `results/predictions/covid-event-pubmedbert/tsv` Each line has:
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
