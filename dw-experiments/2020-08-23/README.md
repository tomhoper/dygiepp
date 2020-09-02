## Description

Train models on either:
- The gold data alone, or
- The gold data, plus weakly-supervised Spike annotations.

For the spike annotations, we down-weight the samples so they don't swamp the gold data. I try weights of 10^0 (no down-weighting), 10^-2, and 10^-4.

We examine performance on the gold dev set.

## Data

- `raw`: Raw data, copied over from elsewhere.
  - `spike`
    - `train.jsonl`: Taken from `spike_train_20200822.jsonl` via google drive: https://drive.google.com/file/d/1yV3WwrXSNCgetfDYr-z4A6DeYBalCjtI/view?usp=sharing.
  - `covid`: Copied from `allgood:/data/aida/covid_clean/UnifiedData/covid_anno_par_s_final/mapped/mech_effect`.
- `cleanup`
  - Remove `section` from the covid data.
  - Remove the NER annotations from the spike data. UPDATE (09-01) these are kept now. The NER's were stored in pairs matching the relation mentions. Ideal with this by flattening the list.
  - Throw out spike entries that have empty strings in them after tokenizing (by whitespace splitting). This discards 160 / 14,766 examples.
  - Also throw out Spike entries with tokens not in the BERT vocab; these break things. Only discards a handful of examples.
- `collated`: Collate the data for faster training.
- `processed`: Add loss weights. Weights are always 1 for covid annotations. There are 4 train datasets:
  - `train.json`: Covid, no spike.
  - `train-spike-0.json`: Include spike data, with loss weights of 10^0 (i.e. 1).
  - `train-spike-2.json`: Include spike data, with loss weights of 10^-2.
  - `train-spike-4.json`: Include spike data, with loss weights of 10^-4.


## Scripts

- `01_merge_spike.py`: Merges in the spike data with the gold data, cleans up, and collates into GPU-sized batches.
- `02_run_evaluation.py`: Evaluate model performance on dev set (test set has no labels). Results go in `results/metrics`.
- `03_merge_metrics.py`: Merge dev set results together. Results go in `results/dev-metrics.tsv`.
- `04_predict.py`: Make predictions using all 4 models on the gold dev and test set (copied from `UnifiedData/covid_anno_par_s_final/mapped/mech_effect`). Then uncollate the results. The predictions go in `results/predictions/(collated|final)`. The dev and test set predictions for each of the settings go in a subfolder:
  - `no-spike`: Train on gold covid, no spike.
  - `spike-0`: Include spike data during training, with loss weights of 10^0 (i.e. 1).
  - `spike-2`: Include spike data during training, with loss weights of 10^-2.
  - `spike-4`: Include spike data during training, with loss weights of 10^-2.
