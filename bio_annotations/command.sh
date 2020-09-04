prodigy rel.manual ner_rels_bio blank:en ./bio_selected.json --label USED, --span-label TASK,METHOD
prodigy relation testdb ./bio_selected.jsonl -F custom_rel.py
prodigy rel.manual t blank:en ./bio_selected0.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY

prodigy rel.manual ner_rels_bio_arezou blank:en ./bio_selected2.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY
prodigy rel.manual ner_rels_bio_madeline blank:en ./bio_selected3.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY
prodigy rel.manual ner_rels_bio_emma blank:en ./bio_selected4.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY --host 3030
prodigy rel.manual ner_rels_bio_jolie blank:en ./bio_selected5.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY --host 4040

prodigy rel.manual ner_rels_bio_jeff blank:en ./bio_selected6.jsonl --label USED,EFFECT,DO --span-label ENTITY --host 3050
prodigy rel.manual ner_rels_bio_megan blank:en ./bio_selected7.jsonl --label USED,EFFECT,DO --span-label ENTITY --host 3060

prodigy rel.manual ner_rels_bio_n1 blank:en ./bio_selected0.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY --host 5000


prodigy rel.manual ner_rels_bio_yeal blank:en ./bio_selected5.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY --host 4040
prodigy rel.manual ner_rels_bio_sara blank:en ./bio_selected2.jsonl --label USED,EFFECT,DO --span-label ENTITY



--validation
prodigy rel.manual madeline_validation blank:en ./validate.jsonl --label USED,EFFECT,DO --span-label ENTITY


madeline_correction --> port 3010
prodigy rel.manual ner_rels_bio_madeline_new blank:en ./correction_annotations_madeline.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY



megan_correction --> port 3020
prodigy rel.manual ner_rels_bio_megan_new blank:en ./correction_annotations_megan.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY


sara_correction --> port 3030
prodigy rel.manual ner_rels_bio_sara_new blank:en ./correction_annotations_sara.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY


prodigy rel.manual ner_rels_bio_tom_test_sara blank:en ./correction_annotations_sara.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY

sara annotations --> port 5080
prodigy rel.manual ner_rels_bio_sara_v2 blank:en ./bio_selected4.jsonl --label USED,EFFECT,DO --span-label ENTITY


yeal annotations --> port 5060
prodigy rel.manual ner_rels_bio_yeal blank:en ./bio_selected10.jsonl --label USED,EFFECT,DO --span-label ENTITY
##################################################################### bad az kharab kari
SARA:
annotation:  port 5080
prodigy rel.manual ner_rels_bio_sara blank:en ./bio_selected4.jsonl --label USED,EFFECT,DO --span-label ENTITY
correction: port 3030 :
prodigy rel.manual ner_rels_bio_sara_correction blank:en correction_input_sara.jsonl --label USED,EFFECT,DO --span-label ENTITY


MEGAN
annotation:  port 3060
prodigy rel.manual ner_rels_bio_megan blank:en ./bio_selected7.jsonl --label USED,EFFECT,DO --span-label ENTITY 
correction:  3020
prodigy rel.manual ner_rels_bio_megan_correction blank:en correction_input_megan.jsonl --label USED,EFFECT,DO --span-label ENTITY


yeal  
annotation : 5060
prodigy rel.manual ner_rels_bio_yeal blank:en ./bio_selected10.jsonl --label USED,EFFECT,DO --span-label ENTITY


MADELINE
annotation : 5050
prodigy rel.manual ner_rels_bio_madeline blank:en ./bio_selected11.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY
correction:  3010
prodigy rel.manual ner_rels_bio_madeline_correction blank:en correction_input_madeline.jsonl --label USED,EFFECT,DO --span-label ENTITY
validation 3000:
prodigy rel.manual ner_rels_bio_madeline_correction blank:en validation_input_madeline.jsonl --label USED,EFFECT,DO --span-label ENTITY
 prodigy rel.manual ner_rels_bio_madeline_correction blank:en validation_input_madeline.jsonl --label USED,EFFECT,DO --span-label ENTITY


TOM
annotations : 1111
prodigy rel.manual ner_rels_bio_tom blank:en ./bio_selected12.jsonl --label USED-TO,EFFECT,DO --span-label ENTITY


tom:
prodigy rel.manual method_measure_tom blank:en ./human_annotations.jsonl --label USED-TO --span-label ENTITY
curation annotations port 2222:
prodigy rel.manual ner_rels_bio_tom_correction blank:en ./tom_curation2_file.jsonl --label USED,EFFECT,DO --span-label ENTITY
prodigy rel.manual ner_rels_bio_tom_correction blank:en ./validation_input_tom_jeff.jsonl --label USED,EFFECT,DO --span-label ENTITY
prodigy rel.manual tt blank:en ./test.jsonl --label USED,EFFECT,DO --span-label ENTITY

tom jeff validation  2223
prodigy rel.manual ner_rels_bio_tom_correction blank:en ./validation_input_tom_kristina.jsonl --label USED,EFFECT,DO --span-label ENTITY
tom kristina validation 2224


tom_curation2_file
prodigy rel.manual tom_stiching_test blank:en ./for_tom_to_correct.jsonl --label USED,EFFECT,DO --span-label ENTITY
prodigy rel.manual tom_event blank:en ./tom_output_total.jsonl --label USED,EFFECT,DO,TRIGGER_ARG0,TRIGGER_ARG1 --span-label ENTITY,TRIGGER


prodigy rel.manual eval_sent blank:en ./human_annotations_sentences.jsonl --label MECHANISM --span-label ENTITY



