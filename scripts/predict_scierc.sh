if [ $3 = "mech" ]
then
       allennlp pretrained/scierc-lightweight.tar.gz \
              $1 \
              --predictor dygie \
              --include-package dygie \
              --use-dataset-reader \
              --output-file \
              $2/scierc/mapped/mech/pred.json \
              --cuda-device \
              $4
       python dygie_pred_to_tsv.py --data_combo scierc --root $2
       python eval_metric.py --data_combo scierc --root $2  
else
       echo allennlp predict pretrained/scierc-lightweight.tar.gz $1 --predictor dygie --include-package dygie --use-dataset-reader --output-file $2/scierc/mapped/mech_effect/pred.json --cuda-device $4
fi
