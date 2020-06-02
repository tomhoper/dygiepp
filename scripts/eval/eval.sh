python eval.py --pred_path $1  --serialdir $2
source activate $3
python eval_metric.py --pred_path $1 


# sh scripts/eval/eval.sh predictions_mech/pred_test.jsonl /data/aida/covid_exp/scierc_covid_anno_par/mech_effect/combo/scierc_covid_anno_par/ covid_eval
# sh  [prediction_path] [serialdir] [conda_eval enviroment name]
