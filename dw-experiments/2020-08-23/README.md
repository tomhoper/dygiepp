## Data

- `raw`: Raw data, copied over from elsewhere.
  - `spike`
    - `train.jsonl`: Taken from `spike_train_20200822.jsonl` via google drive: https://drive.google.com/file/d/1yV3WwrXSNCgetfDYr-z4A6DeYBalCjtI/view?usp=sharing.
  - `covid`: Copied from `allgood:/data/aida/covid_clean/UnifiedData/covid_anno_par_s_final/mapped/mech_effect`.
- `cleanup`
  - Remove `section` from the covid data.
  - Remove the NER annotations from the spike data.
  - Throw out spike entries that have empty strings in them after tokenizing (by whitespace splitting). This discards 160 / 14,766 examples.
- `collated`: Collate the data for faster training.
- `processed`: Add loss weights. Weights are always 1 for covid annotations. There are 4 train datasets:
  - `train.json`: Covid, no spike.
  - `train-spike-0.json`: Include spike data, with loss weights of 10^0 (i.e. 1).
  - `train-spike-2.json`: Include spike data, with loss weights of 10^-2.
  - `train-spike-4.json`: Include spike data, with loss weights of 10^-4.


## Scripts
