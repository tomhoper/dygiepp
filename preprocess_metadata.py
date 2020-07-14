import pandas as pandas
import spacy
import json
from glob import glob

OUT_DIR = "/data/aida/cord19/results_complete/input-meta"
NLP = spacy.load("en_core_web_sm")


def process_paragraph(paragraph):
    res = []
    text = NLP(paragraph)
    # import pdb; pdb.set_trace()
    # print(len(text.sents))
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        all_tokens = all_tokens + tokens
        if len(tokens) < 500:
            res.append(tokens)
        else:
            while tokens:
                res.append(tokens[:500])
                tokens = tokens[500:]

    return res


def process_abstract(abstract, paper_id):
    sents = process_paragraph(abstract)
    return dict(doc_key=f"{paper_id}:abstract",
                section="Abstract",
                sentences=sents)

def read_from_meta_data():
    data = pandas.read_csv("/data/aida/cord19/2020-07-06/metadata.csv")
    data = data.fillna("")
    data = data.loc[data['abstract'] != ""]
    for i, row in data.iterrows():
      # import pdb;pdb.set_trace()
      processed_abstract = process_abstract(row["abstract"], row['cord_uid'])
      newname = row['cord_uid'] + ".jsonl"
      with open(f"{OUT_DIR}/{newname}", "w") as f:
          print(json.dumps(processed_abstract), file=f)

      print(f"{row['cord_uid']}: success")

def merge_docs():
    names = glob("/data/aida/cord19/results_complete/input-meta/*.jsonl")
    # output_file = open("/data/aida/cord19/cord_abstracts_100k.jsonl", "w")
    total_docs = []
    print(len(names))
    for file in names:
      print(file)
      docs = [json.loads(line) for line in open(file)]
      total_docs = total_docs + docs
    with open("/data/aida/cord19/cord_abstracts_100k.jsonl", 'w') as outfile:
      for element in total_docs:
        json.dump(element, outfile)
        outfile.write("\n")

def divide_training_prediction():
  input_file = open("/data/aida/cord19/cord_abstracts_100k.jsonl")
  line_count = 0
  index = 0
  for line in input_file:
    print(line_count)
    if line_count % 1000 == 0:
      output_file = open("/data/aida/cord19/partitions/cord_abstracts_100k_removed_annotation_partition" + str(index) + ".jsonl", "w")
      index += 1
    output_file.write(line)
    line_count += 1

def remove_annotations():
  return 0


if __name__ == "__main__":
    # read_from_meta_data()
    merge_docs()













