Make coref predictions on large collection of abstracts, and merge clusters on "most representative member".

## Scripts

- `01_create_shards.py`: Create 4 evenly-sized data shards as GPU inputs. Throw out documents that have sentences with only a single token; coref breaks on these.
  - Inputs: `data/partitions_small`, which comes from `allgood:/data/aida/cord19_sentences/partitions_small`. Use CPU; run predictions in parallel.
  - Outputs: `data/shards`, which has 4 equal-sized files.
- `02_predict.py`: Make predictions on the 4 shards of data, using both of the models (SciERC-trained only and SciERC+GENIA)
  - Inputs: `data/shards`
  - Outputs: `results/predictions`; one per shard and model.
- `03_collect_shards`: Collect the predictions from all shards and from the two models.
  - Inputs: `results/predictions`
  - Outputs: In `results/predictions-collected`.
    - The failed predictions are in `failed-txt`.
- `04_to_tsv.py`: Convert to `.tsv` format, same as from 09-01.
  - Outputs: The `tsv` files in `results/predictions-collected`.
