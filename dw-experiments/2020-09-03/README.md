Make coref predictions on large collection of abstracts, and merge clusters on "most representative member".

## Scripts

- `01_create_shards.py`: Create 4 evenly-sized data shards as GPU inputs. Throw out documents that have sentences with only a single token; coref breaks on these.
  - Inputs: `data/partitions_small`, which comes from `allgood:/data/aida/cord19_sentences/partitions_small`. Use CPU; run predictions in parallel.
  - Outputs: `data/shards`, which has 4 equal-sized files.
- `02_predict.py`: Make predictions on the 4 shards of data, using both of the models (SciERC-trained only and SciERC+GENIA)
  - Inputs: `data/shards`
