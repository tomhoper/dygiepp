import utils as ut
import pathlib
from pathlib import Path
import json



def update_annotations_corrections():
    # ut.update_extractions(ut.DEFAULT_NAME_LIST, ut.ANNOTATION_DIR_PATH, annotations_correction="annotations")
    # ut.update_extractions(ut.DEFAULT_CORRECTION_NAME_LIST, ut.CORRECTION_DIR_PATH, annotations_correction="correction")
    ut.merge_with_old(ut.ANNOTATION_DIR_PATH + "jsons/", ut.ANNOTATION_DIR_PATH_OLD + 'jsons/')
    ut.merge_with_old(ut.CORRECTION_DIR_PATH + "jsons/", ut.CORRECTION_DIR_PATH_OLD + 'jsons/')

    for name in ut.DEFAULT_NAME_LIST:
        annotation_name = 'annotations_' + name + '.jsonl'
        annotation_name_tsv = 'annotations_' + name + '.tsv'
        annotation_json_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "jsons" / annotation_name
        annotation_tsv_file = pathlib.Path(ut.ANNOTATION_DIR_PATH) / "tsvs" / annotation_name_tsv
        ut.visualize_the_annotations_to_tsv2(annotation_json_file, annotation_tsv_file, name)
    for name in ut.DEFAULT_CORRECTION_NAME_LIST:
        annotation_name = 'corrections_' + name + '.jsonl'
        annotation_name_tsv = 'corrections_' + name + '.tsv'
        correction_json_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "jsons" / annotation_name
        correction_tsv_file = pathlib.Path(ut.CORRECTION_DIR_PATH) / "tsvs" / annotation_name_tsv
        ut.visualize_the_annotations_to_tsv2(correction_json_file, correction_tsv_file, name)

def write_annotations_for_tom(input_filename):
    input_file = open(input_filename)
    key_text_pair_seen = ('','')
    relation_info = []
    count = 0 # to add the lines more than 274
    already_annotated_list = ut.read_already_annotated(["ner_rels_bio_tom_correction"])
    print(len(already_annotated_list))
    output_file = open("tom_curation_file.jsonl", "w")
    seen_list = [0 for x in range(len(already_annotated_list))]
    edit_needed = False
    for line in input_file:
        count += 1
        # import pdb; pdb.set_trace()
        doc_id, text, arg0, arg1, rel, accept, _, edit, comment = line.split('\t')[:9]
        if accept == "reject":
            continue
        if (doc_id, text) != key_text_pair_seen:
            if key_text_pair_seen != ('',''):
                res = ut.convert_to_json(key_text_pair_seen[1], relation_info, key_text_pair_seen[0])
                if (edit_needed or count > 273) and (key_text_pair_seen[0], key_text_pair_seen[1]) not in already_annotated_list:
                    json.dump(res, output_file)
                    output_file.write('\n')
            relation_info = []
            edit_needed = False
            if edit != '':
                edit_needed = True
            key_text_pair_seen = (doc_id, text)
            relation_info.append((rel, arg0, arg1))
        else: 
            if edit != '':
                edit_needed = True
            relation_info.append((rel, arg0, arg1))

    res = ut.convert_to_json(key_text_pair_seen[1], relation_info, key_text_pair_seen[0])
    if (edit_needed or count > 273) and (key_text_pair_seen[0], key_text_pair_seen[1]) not in already_annotated_list:
        json.dump(res, output_file)
        output_file.write('\n')
    import pdb; pdb.set_trace()
# update_annotations_corrections()
write_annotations_for_tom('tom_curation.tsv')
