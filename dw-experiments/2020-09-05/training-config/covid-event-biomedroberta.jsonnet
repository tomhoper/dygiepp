local template = import "template.libsonnet";

template.DyGIE {
  bert_model: "allenai/biomed_roberta_base",
  cuda_device: 1,
  data_paths: {
    train: "data/processed/collated/train.jsonl",
    validation: "data/processed/collated/dev.jsonl",
    test: "data/processed/collated/test.jsonl",
  },
  loss_weights: {
    ner: 0.0,
    relation: 0.0,
    coref: 0.0,
    events: 1.0
  },
  target_task: "events",
  model +: {
    modules +: {
      events +: {
        loss_weights: {
          trigger: 0.1,
          arguments: 1.0
        },
      },
    },
  }
}
