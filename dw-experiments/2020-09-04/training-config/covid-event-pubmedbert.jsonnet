local template = import "template.libsonnet";

template.DyGIE {
  bert_model: "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
  cuda_device: 0,
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
