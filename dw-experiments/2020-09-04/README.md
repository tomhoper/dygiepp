Convert Tom's event annotations to DyGIE format and train model on them.


## Experiment description

- Preprocess Tom's event annotations as described in [annotation notse from Tom](#annotation-notes-from-tom)
- Split into train, dev, test.
- Train event extraction model (using BioMedRoberta and PubMedBert).
- Evaluate results.


## Results

|                      |   biomedroberta |   pubmedbert |
|----------------------|-----------------|--------------|
| trig_class_precision |          0.6442 |       0.6447 |
| trig_class_recall    |          0.6700 |       0.6833 |
| trig_class_f1        |          0.6569 |       0.6634 |
| arg_class_precision  |          0.5504 |       0.5795 |
| arg_class_recall     |          0.5034 |       0.5062 |
| arg_class_f1         |          0.5259 |       0.5404 |


## Scripts

- `01_convert.py`: Convert to our format.
  - Inputs: The event annotations are copied from `allgood:/home/aida/covid_clean/dygiepp/bio_annotations/tom_event.jsonl`. I put it in `data/raw`.
  - Notes: As per Tom's message,
  - Outputs: `data/processed/events.jsonl`
- `02_split_and_collate.py`: Split into train / dev / test and collate.
  - Inputs: `data/processed/events.jsonl`
- `train.sh`: Run training.
  - Outputs: `models`
- `evaluate.sh`: Run test set evaluation.
  - Outputs: `results/metrics`
- `03_check_folds.py`: The results are so good, I wanted to double-check that the folds are disjoint.
- `04_collect_results.py`: Make a table.
  - Outputs: `results/summary.tsv`, `results/summary.md` (shown above).


## Annotation notes from Tom

- Ignore relations between two `ENTITY`'s and only look at relations between a `TRIGGER` and an `ENTITY`.
- Here's the way to generate SciERC events from these annotations:
  - for every TRIGGER entity t,
    - for every  TRIGGER_ARG0 relation outgoing from t to entity e0,
      - for every  TRIGGER_ARG1 relation outgoing from t to entity e1 ,
        - create “event” e <- [e0, t, e1]
