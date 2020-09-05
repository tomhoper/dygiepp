Convert Tom's event annotations to DyGIE format and train model on them.

## Scripts

- `01_convert.py`: Convert to our format.
  - Inputs: The event annotations are copied from `allgood:/home/aida/covid_clean/dygiepp/bio_annotations/tom_event.jsonl`. I put them in `data`.
  - Notes: As per Tom's message,


## Annotation notes from Tom

- Ignore relations between two `ENTITY`'s and only look at relations between a `TRIGGER` and an `ENTITY`.
- Here's the way to generate SciERC events from these annotations:
  - for every TRIGGER entity t,
    - for every  TRIGGER_ARG0 relation outgoing from t to entity e0,
      - for every  TRIGGER_ARG1 relation outgoing from t to entity e1 ,
        - create “event” e <- [e0, t, e1]
