local template = import "/home/aida/covid_clean/dygiepp/training_config/template_event_allentune.libsonnet";

template.DyGIE {
  bert_model: "allenai/scibert_scivocab_cased",
  cuda_device: 1,
  data_paths: {
    train: "/home/aida/covid_clean/dygiepp/data/processed/collated/train.json",
    validation: "/home/aida/covid_clean/dygiepp/data/processed/collated/dev.json",
    test: "/home/aida/covid_clean/dygiepp/data/processed/collated/test.json",
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
