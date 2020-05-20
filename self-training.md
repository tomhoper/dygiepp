A few notes on how to use this branch to do iterative self-training.

The NER and relation labels should all be prefixed with the dataset they were derived from, for instance:
- `chemprot:CHEMICAL` or `scierc:USED-FOR`.

The model expects either training data, or test data.

For the training data, the `doc_keys` for each entry should be written as follows:
- Original data: `[dataset]:[original_doc_key]`. For instance, `chemprot:15985434` or `scierc:H05-1095`.
- For self-training data (data with labels predicted by the model), the doc_key should be `self-train:[dataset]:[original_doc_key]`. For instance, `self-train:chemprot:15985434`.

When computing the loss incurred by model predictions, the model will only evaluate predictions on original data against the labels from the matching dataset. For self-training data, the model will evaluate the predictions against all labels (from all datasets). The model will predict a single NER label for each text span.

For test data, the `doc_keys` should not have any `:`. For test data, the model can predict multiple NER labels for each span.
