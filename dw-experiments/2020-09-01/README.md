Make coreference predictions on Aida's data, merge into a `.csv`, and send back.

## File dependencies

- The files in `data/jsons` are copied from `allgood:/data/aida/covid_annotation_data/jsons`.
- I merge them all together in `data/merged.jsonl`


## Scripts

- `01_format_data.py`: Concatenate all input docs and add a `dataset` field to the input so that the model knows to match it with the SciERC namespace.
  - Inputs: `data/jsons/[input-files]`
  - Outputs: `data/merged.jsonl`
- `02_predict_coref.sh`: Make coref predictions using both a model trained on `scierc` only, and a model trained on `genia` + `scierc`.
  - Inputs: `data/merged.jsonl`
  - Outputs: `results/predictions/[model-name].jsonl`.
- `03_evaluate_on_scierc.py`: The predictions from the two different models are pretty different, so I'm going to do some diagnostics to see which is better. First step: use them both to predict coref on SciERC and compare their scores.
  - Inputs: SciERC data.
  - Outputs: `results/scierc-performance/[model-name].jsonl`
  - Results: The GENIA + SciERC model is marginally better.
    - Model trained on SciERC only gets coref P, R, F1 of (55, 47, 51)
    - Model trained on GENIA + SciERC gets (58, 47, 52).
- `04_predict_scierc.sh`: Also make coref predictions for both models on the SciERC dataset.
  - Outputs: `results/predictions-scierc/[model-name].jsonl`
- `05_compute_similarity.py`: Look at similarity between the predictions of the two different models, on both SciERC and Covid data.
  - Inputs: `results/predictions` and `results/predictions-scierc`.
  - Outputs: `results/prediction-similarity.tsv`
  - Results
    - The models have reasonable similarity on SciERC (F1=0.56).
    - But on COVID, their similarity is much lower (F1=0.20).
- `06_analyze_differences.py`: Look at the differences in prediction between the two models.
  - Results: `results/prediction-differences.pdf`.
- `07_merge.py`: Merge together the two sets of coref predictions. I use the following procedure to merge the coref clusters from the two predictions (call them `doc1` and `doc2`):
  - If there is an exact match between a span in `doc1` and a span in `doc2`, merge the clusters containing these spans. Then, iteratively merge in any additional clusters that match one of the spans in the new, merged clusters.
  - Remove any clusters for which no match was found.
- `08_count_merged.py`: Count how many spans and clusters are left in the merged data.
  |            |   scierc |   merged |   genia-scierc |
  |------------|----------|----------|----------------|
  | n_clusters |      526 |      172 |            595 |
  | n_spans    |     2002 |      969 |           1644 |
- `09_to_tsv.py`: Dump output to `.tsv`. Results go in `rseults/predictions`. Schema:
  ```text
  doc_key  cluster_id  cluster_exemplar  cluster_members ...
  ```


## Concrete example of cluster merging

```python
# Coref clusters indicated by token indices (for this example, token indices are simpler than spans).
doc1 = [[11, 13], [12, 15]]
doc2 = [[13, 15, 16], [18, 20]]

# Merge first cluster in doc1 and first cluster in doc2, since they match on token 13.
merged = [11, 13, 15, 16]

# Now, the second cluster in doc 1 can also be merged into this cluster, since it matches with the merged cluster on token 15.
merged = [11, 12, 13, 14, 16]

# The second cluster in doc2 doesn't have a match in doc 1, so we don't include it.
return [merged]
```
