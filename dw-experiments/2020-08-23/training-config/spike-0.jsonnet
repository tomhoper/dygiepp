local template = import "template.libsonnet";

template.DyGIE {
  bert_model: "allenai/scibert_scivocab_cased",
  cuda_device: 2,
  data_paths: {
    train: "data/processed/train-spike-0.json",
    validation: "data/processed/dev.json",
    test: "data/processed/test.json",
  },
  loss_weights: {
    ner: 0.5,
    relation: 1.0,
    coref: 0.0,
    events: 0.0
  },
  target_task: "relation",
}
