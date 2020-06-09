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
