# python predict.py --root /data/aida/covid_clean  --data_combo scierc_covid_anno_par --mech_effect_mode
python eval_metric.py --root /data/aida/covid_clean  --data_combo scierc_covid_anno_par --mech_effect_mode
# python predict.py --root /data/aida/covid_clean  --data_combo scierc_covid_anno_par --mech_effect_mode
python eval_metric.py --root /data/aida/covid_clean  --data_combo scierc_covid_anno_augmented_par --mech_effect_mode


python eval_metric.py --root /data/aida/covid_clean  --data_combo scierc_covid_anno_par 


#for dygie


allennlp predict pretrained/scierc.tar.gz \
/data/aida/covid_clean/UnifiedData/covid_anno_par/mapped/mech_effect/test.json \
--predictor dygie \
--include-package dygie \
--use-dataset-reader \
--output-file /data/aida/covid_clean/predictions/pred_dygie_orig_scierc.json \
--cuda-device 0
