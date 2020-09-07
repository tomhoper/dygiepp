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
       allennlp predict pretrained/scierc-lightweight.tar.gz $1 --predictor dygie --include-package dygie --use-dataset-reader --output-file $2/scierc/mapped/mech_effect/pred.json --cuda-device $4
       python dygie_pred_to_tsv.py --data_combo scierc --root $2 --mech_effect_mode
       echo python eval_metric.py --data_combo scierc --root $2  --mech_effect_mode
fi

#mech effect predictions
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_final/mapped/mech_effect/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_final/mapped/mech_effect/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_final_stichings/mapped/mech_effect/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_final_stichings/mapped/mech_effect/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_sentence_madeline_final/mapped/mech_effect/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_sentence_madeline_final/mapped/mech_effect/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_sentence_madeline_final_tom_stiching/mapped/mech_effect/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_sentence_madeline_final_tom_stiching/mapped/mech_effect/pred.json --cuda-device 3


#mech effect predictions

 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_final/mapped/mech/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_final/mapped/mech/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_final_stichings/mapped/mech/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_final_stichings/mapped/mech/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_sentence_madeline_final/mapped/mech/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_sentence_madeline_final/mapped/mech/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_sentence_madeline_final_tom_stiching/mapped/mech/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_sentence_madeline_final_tom_stiching/mapped/mech/pred.json --cuda-device 3

 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_sentences_matchcd/mapped/mech/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_sentences_matchcd/mapped/mech/pred.json --cuda-device 3
 allennlp predict pretrained/scierc-lightweight.tar.gz /data/aida/covid_aaai/UnifiedData/covid_anno_par_madeline_sentences_matchcd/mapped/mech_effect/test.json --predictor dygie --include-package dygie --use-dataset-reader --output-file /data/aida/covid_aaai/predictions/scierc_pretrained/covid_anno_par_madeline_sentences_matchcd/mapped/mech_effect/pred.json --cuda-device 3
 

 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_sentences_matchcd --root /data/aida/covid_aaai/predictions/scierc_pretrained --mech_effect_mode
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_sentences_matchcd --root /data/aida/covid_aaai/predictions/scierc_pretrained
python eval_metric.py --data_combo covid_anno_par_madeline_sentences_matchcd --root /data/aida/covid_aaai/  --mech_effect_mode --gold_combo gold_madeline_sentences_matchcd




 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_final --root /data/aida/covid_aaai/predictions/scierc_pretrained --mech_effect_mode
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_final_stichings --root /data/aida/covid_aaai/predictions/scierc_pretrained --mech_effect_mode
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_sentence_madeline_final --root /data/aida/covid_aaai/predictions/scierc_pretrained --mech_effect_mode
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_sentence_madeline_final_tom_stiching --root /data/aida/covid_aaai/predictions/scierc_pretrained --mech_effect_mode
 
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_final --root /data/aida/covid_aaai/predictions/scierc_pretrained
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_madeline_final_stichings --root /data/aida/covid_aaai/predictions/scierc_pretrained
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_sentence_madeline_final --root /data/aida/covid_aaai/predictions/scierc_pretrained
 python dygie_pred_to_tsv.py --data_combo covid_anno_par_sentence_madeline_final_tom_stiching --root /data/aida/covid_aaai/predictions/scierc_pretrained



python eval_metric.py --data_combo covid_anno_par_madeline_final --root /data/aida/covid_aaai/  --mech_effect_mode --gold_combo gold_madeline_final
python eval_metric.py --data_combo covid_anno_par_madeline_final_stichings --root /data/aida/covid_aaai/  --mech_effect_mode --gold_combo gold_madeline_final_stichings
python eval_metric.py --data_combo covid_anno_par_sentence_madeline_final --root /data/aida/covid_aaai/  --mech_effect_mode --gold_combo gold_sentence_madeline_final
python eval_metric.py --data_combo covid_anno_par_sentence_madeline_final_tom_stiching --root /data/aida/covid_aaai/  --mech_effect_mode --gold_combo gold_sentence_madeline_final_tom_stiching

python eval_metric.py --data_combo covid_anno_par_madeline_final --root /data/aida/covid_aaai/  --gold_combo gold_madeline_final
python eval_metric.py --data_combo covid_anno_par_madeline_final_stichings --root /data/aida/covid_aaai/  --gold_combo gold_madeline_final_stichings
python eval_metric.py --data_combo covid_anno_par_sentence_madeline_final --root /data/aida/covid_aaai/  --gold_combo gold_sentence_madeline_final
python eval_metric.py --data_combo covid_anno_par_sentence_madeline_final_tom_stiching --root /data/aida/covid_aaai/  --gold_combo gold_sentence_madeline_final_tom_stiching



predictions/scierc_pretrained
predictions/scierc_pretrained
predictions/scierc_pretrained
predictions/scierc_pretrained
predictions/scierc_pretrained
predictions/scierc_pretrained
predictions/scierc_pretrained
