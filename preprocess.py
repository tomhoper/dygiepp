"""
Preprocess data from LaTex parses. Need to run on S3 machine 3, that's where the
data are.
"""
ANNOTATION_PATH = "../covid_clean_data/data/covid/json/bio_annotations/annotated_complete.tsv"

import os
import multiprocessing
import pandas as pd
import spacy
from glob import glob
import time
import json
from collections import Counter
import random
random.seed(100)

# counts = Counter()

# DATA_PATH = "2020-03-13"
# OUT_DIR = "results_complete/input-json"
NLP = spacy.load("en_core_web_sm")

# os.makedirs(OUT_DIR, exist_ok=True)

# folders = os.listdir(DATA_PATH)


def tokenize(sent):
    # Sometimes the grobid parse crashes and gives outrageously long sentences.
    # If they're long, split. So this returns a list of lists, just in case the
    # sentences need to be split. If no splitting, it's just a list containing a
    # single list.
    processed = NLP(sent)
    tokens = [x.text for x in processed]

    # If it's not too long, return it.
    if len(tokens) < 100:
        return [tokens]

    # Otherwise split it by sentence and return.
    res = []
    for entry in processed.sents:
        tokens = [x.text for x in entry]
        # If it's less than 100 after splitting, append the sentence.
        if len(tokens) < 100:
            res.append(tokens)
        # Otherwise, just split it into chunks of 100.
        else:
            while tokens:
                res.append(tokens[:100])
                tokens = tokens[100:]

    return res


def process_paragraph(paragraph):
    res = []
    text = NLP(paragraph)
    # import pdb; pdb.set_trace()
    # print(len(text.sents))
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        all_tokens = all_tokens + tokens
        # if len(tokens) < 500:
        #     res.append(tokens)
        # else:
        #     while tokens:
        #         res.append(tokens[:500])
        #         tokens = tokens[500:]

    return [all_tokens]


def process_abstract(abstract, paper_id):
    sents = process_paragraph(abstract[0]['text'])
    return dict(doc_key=f"{paper_id}:abstract",
                section="Abstract",
                sentences=sents)

def process_abstract_metadata_file(abstract, paper_id):
    # import pdb; pdb.set_trace()
    sents = process_paragraph(abstract)
    return dict(doc_key=f"{paper_id}_abstract",
                section="Abstract",
                sentences=sents)


def get_latex_text(para):
    raw_text = para["text"]
    return raw_text

    # replacements = []
    # for eq_span in para["eq_spans"]:
    #     in_raw = raw_text[eq_span["start"]:eq_span["end"]]
    #     replacement = eq_span["text"]
    #     if "INLINEFORM" in in_raw and replacement is not None:
    #         replacements.append((in_raw, replacement))

    # output_text = raw_text

    # for old_text, new_text in replacements:
    #     output_text = output_text.replace(old_text, new_text)

    # return output_text


def process_body(body_text, paper_id):
    all_paragraphs = []
    for i, para in enumerate(body_text):
        # text = get_latex_text(para)
        sents = process_paragraph(body_text)
        to_append = dict(doc_key=f"{paper_id}:body_text:{i}",
                         section="abstract",
                         sentences=sents)
        all_paragraphs.append(to_append)

    return all_paragraphs


def process_article(paper):
    "Handle a single paper."
    name = os.path.basename(paper).replace(".json", "")

    data = json.load(open(paper))
    paper_id = data["paper_id"]

    # If no metadata, skip it.
    metadata = data["metadata"]
    if "abstract" not in data or not data["abstract"]:
        print(f"{name}: no abstract")
        return name, "no_abstract"
        # abstract = [{"text": ""}]
    else:
        abstract = data["abstract"]

    # import pdb; pdb.set_trace()  
    # If no body text, skip it.
    body_text = data["body_text"]
    if not body_text:
        print(f"{name}: no body")
        return name, "no_body"

    try:
        processed_abstract = process_abstract(abstract, paper_id)
        processed_body = process_body(body_text, paper_id)
    except Exception:
        print(f"{name}: failed processing")
        return name, f"failed_processing:"

    to_write = [processed_abstract] + processed_body

    # Simple length check.
    assert len(to_write) == 1 + len(body_text)

    # Write to .jsonl file.
    newname = name + ".jsonl"
    with open(f"{OUT_DIR}/{newname}", "w") as f:
        for entry in to_write:
            print(json.dumps(entry), file=f)

    # Return success code.
    print(f"{name}: success")
    return name, "success"

def process_metadata_csv(file_name):
    import csv
    header_seen = False
    abstract_index = -1
    paper_id_index = -1
    with open(file_name, newline='') as f:
        reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_NONE)
        for row in reader:
            row = row[0].split("\t")
            if header_seen == False:

                header_seen = True
                abstract_index = row.index("abstract")
                paper_id_index = row.index("cord_uid")
                continue
            # import pdb; pdb.set_trace()
            if len(row) <= abstract_index:
                continue
            abstract = row[abstract_index]
            if abstract == "":
                continue
            paper_id = row[paper_id_index]
            try:
                processed_abstract = process_abstract_metadata_file(abstract, paper_id)
            except Exception:
                print(f"{paper_id}: failed processing")
                continue

            newname = paper_id + ".jsonl"
            with open(f"{OUT_DIR}/{newname}", "w") as f:
                print(json.dumps(processed_abstract), file=f)

            print(f"{paper_id}: success")


def process_abstract_article(paper):
    "Handle a single paper."
    name = os.path.basename(paper).replace(".json", "")

    data = json.load(open(paper))
    paper_id = data["paper_id"]

    # If no metadata, skip it.
    metadata = data["metadata"]
    if "abstract" not in data or not data["abstract"]:
        print(f"{name}: no abstract")
        return name, ""
    else:
        abstract = data["abstract"]

    # If no body text, skip it.

    try:
        processed_abstract = process_abstract(abstract, paper_id)
    except Exception:
        print(f"{name}: failed processing")
        return name, ""

    to_write = [processed_abstract] 

    # Simple length check.
    # assert len(to_write) == 1 + len(body_text)

    # Write to .jsonl file.
    # newname = name + ".jsonl"
    # with open(f"{OUT_DIR}/{newname}", "w") as f:
    #     for entry in to_write:
    #         print(json.dumps(entry), file=f)

    # Return success code.
    print(f"{name}: success")
    return name, processed_abstract



def safe_process_article(name):
    try:
        res = process_article(name)
        return res
    except Exception as e:
        print(f"{name}: unspecified error")
        return name, e.__class__

def find_index(sentence, arg_parts):
  ind_seen = -1
  count = 0
  arg_seen = False
  for i in range(len(sentence)):
    if sentence[i] == arg_parts[0]:
        arg_seen = True
        ind_seen = count
        for k in range(len(arg_parts)):
            if i + k < len(sentence) and arg_parts[k] != sentence[i + k]:
                arg_seen = False
                ind_seen = -1
        if arg_seen == True:
            break
    count += 1
  return ind_seen

def reorder_format(anno_list):
    text_res = process_abstract_metadata_file(anno_list[0][1], anno_list[0][0])
    text_res['relations'] = [[]]
    text_res['ner'] = [[]]
    for annotation in anno_list:
        arg0_parts = process_paragraph(annotation[2])[0]
        arg1_parts = process_paragraph(annotation[3])[0]
        # import pdb; pdb.set_trace()
        ind0 = find_index(text_res['sentences'][0], arg0_parts)
        ind1 = find_index(text_res['sentences'][0], arg1_parts)
        if ind0 == -1 or ind1 == -1:
            print("hereeee")
            continue
        text_res['ner'][0].append([ind0, ind0 + len(arg0_parts), "ENTITY"])
        text_res['ner'][0].append([ind1, ind1 + len(arg1_parts), "ENTITY"])
        if "used" in annotation[4].lower() or 'do' in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts), ind1, ind1 + len(arg1_parts), "MECHANISM"])
        if "effect" in annotation[4].lower() or 'do' in annotation[4].lower():
            text_res['relations'][0].append([ind0, ind0 + len(arg0_parts), ind1, ind1 + len(arg1_parts), "MECHANISM"])
    return text_res
    import pdb; pdb.set_trace()

def create_annotated_covid(noise):
    DATA_PATH= "dygiepp/UnifiedData/covid_anno_par/mapped/mech/"
    DATA_PATH_NOISY= "dygiepp/UnifiedData/covid_anno_augmented_par/mapped/mech/"
    TRAIN_COUNT = 0
    DEV_COUNT = 46
    # TRAIN_COUNT_FROM_NOISE=80

    doc_key_ind = {}
    madeline_keys = []
    other_keys = []
    input_file = open(ANNOTATION_PATH)
    madeline_annotated = {}
    other_annotation = {}
    for line in input_file:
        line_parts = line[:-1].split("\t")
        key = (line_parts[0], line_parts[1])
        # import pdb; pdb.set_trace()
        if line_parts[-1] == "madeline":
            if line_parts[0] not in madeline_keys:
                madeline_keys.append(line_parts[0])
            if key not in madeline_annotated:
                madeline_annotated[key] = []
                madeline_annotated[key].append(line_parts)
            else:
                madeline_annotated[key].append(line_parts)
            if key in other_annotation:
                del other_annotation[key]
        else:
            if line_parts[0] not in other_keys:
                other_keys.append(line_parts[0])
            if key not in madeline_annotated:
                if key not in other_annotation and line_parts[0]:
                    other_annotation[key] = []
                    other_annotation[key].append(line_parts)
                else:
                    other_annotation[key].append(line_parts)

    # reorder_format(line_parts)

    unique_to_madeline = [doc_key for doc_key in madeline_keys if doc_key not in other_keys]
    print(len(unique_to_madeline))
    random.shuffle(unique_to_madeline)
    random.shuffle(madeline_keys)
    random.shuffle(other_keys)
    other_madeline = [doc_key for doc_key in madeline_keys if doc_key not in unique_to_madeline[0:40]]


    output_file_test_noise = open(DATA_PATH_NOISY + "test.json", "w")
    output_file_train_noise = open(DATA_PATH_NOISY + "train.json", "w")
    output_file_dev_noise = open(DATA_PATH_NOISY + "dev.json", "w")

    output_file_test = open(DATA_PATH + "test.json", "w")
    # output_file_train = open(DATA_PATH + "train.json", "w")
    # output_file_dev = open(DATA_PATH + "dev.json", "w")
    print(unique_to_madeline[0:40])
    for key in madeline_annotated:
        data = reorder_format(madeline_annotated[key])
        if key[0] in unique_to_madeline[0:40]: #test data
            json.dump(data, output_file_test)
            json.dump(data, output_file_test_noise)
            output_file_test.write("\n")
            output_file_test_noise.write("\n")
        else:
            if key[0] in other_madeline[0:TRAIN_COUNT]:
                if noise:
                    json.dump(data, output_file_train_noise)
                    output_file_train_noise.write('\n')
                else:
                    json.dump(data, output_file_train)
                    output_file_train.write('\n')
            else:
                if noise:
                    json.dump(data, output_file_dev_noise)
                    output_file_dev_noise.write('\n')
                else:
                    json.dump(data, output_file_dev)
                    output_file_dev.write('\n')
    if noise:
        for key in other_annotation:
            data = reorder_format(other_annotation[key])
            json.dump(data, output_file_train_noise)
            output_file_train_noise.write('\n')
            
    # if noise == False


if __name__ == "__main__":
    # print("hereeeeee")
    # process_metadata_csv("metadata")]
    create_annotated_covid(True)
    # names = glob(f"{DATA_PATH}/*/*/*.json")
    # # names = names[:100]
    # safe_process_article(names[0])

    # # process_article(names[0])
    # workers = multiprocessing.Pool(56)
    # start = time.time()

    # results = workers.map(safe_process_article, names)

    # elapsed = (time.time() - start) / 60

    # print()
    # print(f"Elapsed: {elapsed:0.2f}")

    # results = pd.DataFrame(results, columns=["paper_id", "status"])
    # results.to_csv("results/preprocess-status.tsv", sep="\t", index=False)