#this file is just to fix the issue of broken partitions 
import json
import spacy
from operator import itemgetter
import re
from copy import deepcopy
import utils as ut

NLP = spacy.load("en_core_web_sm")

def process_paragraph(paragraph):
    res = []
    text = NLP(paragraph)
    all_tokens = []
    for sent in text.sents:
        tokens = [x.text for x in sent]
        all_tokens = all_tokens + tokens
    return [all_tokens]

def find_the_ids_with_issues(input_file_path):
    
    docs = [json.loads(line) for line in open(input_file_path)]
    doc_id_list = []
    for doc in docs:
        if not( doc['text'].endswith('.') or  doc['text'].endswith('!') or  doc['text'].endswith('?')):
          if doc['meta']['doc_key'] not in doc_id_list:
            doc_id_list.append(doc['meta']['doc_key'])
    # print((doc_id_list))
    return doc_id_list

def find_all_docs_in_order_by_docid(docs, doc_id, text):
  selected_docs = []
  seen_starts = []
  text = " ".join(process_paragraph(text)[0])
  for doc in docs:
    if doc['meta']['doc_key'] == doc_id:
      if doc["text"] not in text:
        import pdb; pdb.set_trace()
      text_start_ind = text.index(doc["text"])
      if text_start_ind not in seen_starts:
        selected_docs.append((text_start_ind, doc))
        seen_starts.append(text_start_ind)

  sorted_docs = sorted(selected_docs,key=itemgetter(0),reverse=True)
  return sorted_docs    

def read_metadata(metadata_path):
    metadata = {}
    input_file = open(metadata_path)
    for line in input_file:
      line_parts = line[:-1].split('\t')
      if (len(line_parts)) < 3:
        continue
      metadata[line_parts[0]] =  line_parts[2]
    return metadata



def correct_next_doc_removing_first_sentence(doc):
    
    res = deepcopy(doc)
    cutting_ind = doc['text'].index(re.findall("\?|\.|\!", doc['text'])[0])
    extra_string = doc['text'][:cutting_ind+1]

    
  
    if doc['text'][cutting_ind-1:cutting_ind+2] == "0.0":   #edge case
          cutting_ind = doc['text'].index(re.findall("\?|\.|\!", doc['text'])[1], cutting_ind+1)
          extra_string = doc['text'][:cutting_ind+1]
    
    res["text"] = doc['text'][cutting_ind+1:]
    relation_pairs = []
    for rel in res["relations"]:
        if rel['head_span']["end"] < len(extra_string) or rel['child_span']["end"] < len(extra_string):
          continue
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"], relation_pairs, res["meta"]["doc_key"])
    return res, extra_string

def correct_next_doc_adding_first_sentence(doc, extra_string):
    
    res = deepcopy(doc)
    res["text"] = extra_string.strip() + ' ' + doc['text']
    
    relation_pairs = []
    for rel in res["relations"]:
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"], relation_pairs, res["meta"]["doc_key"])
    return res

def correct_before_doc_adding_last_sentence(doc, extra_string):
    
    res = deepcopy(doc)
    res["text"] =  doc['text'].strip() + ' ' + extra_string.strip()
    
    relation_pairs = []
    for rel in res["relations"]:
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"], relation_pairs, res["meta"]["doc_key"])
    return res

def correct_before_doc_removing_last_sentence(doc):
    
    res = deepcopy(doc)
    cutting_ind = doc['text'].rindex(re.findall("\?|\.|\!", doc['text'])[len(re.findall("\?|\.|\!", doc['text'])) - 1])
    extra_string = doc['text'][cutting_ind+1:]
    
    res["text"] = doc['text'][:cutting_ind+1]
    relation_pairs = []
    for rel in res["relations"]:
        if rel['head_span']["start"] > len(res["text"]) or rel['child_span']["start"] > len(res["text"]):
          continue
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"], relation_pairs, res["meta"]["doc_key"])
    return res, extra_string




    # if len(res["text"]) < 2:
    #   return None
    # token_shift = len(extra_string_tokens[0])
    # string_shift = len(extra_string)
    # # Keys that need to be edited: tokens, span, relations
    # # editting tokens
    # for tok in res["tokens"]:
    #   print(tok['id'])
    #   #for tokens the indexings that needs to be fixed are start and end and id
    #   if tok['id'] < token_shift: #deleted token
    #       res["tokens"].remove(tok)
    #   else:
    #     tok['start'] -= string_shift
    #     tok['end'] -= string_shift
    #     tok['id'] -= token_shift

    # for span in res['spans']:
    #   #for span the indexings that needs to be fixed are start and end and token_start and token_en
    #   import pdb; pdb.set_trace()




def write_stiching_docs(metadata_path, input_file_path, id_list):
    docs = [json.loads(line) for line in open(input_file_path)]
    metadata = read_metadata(metadata_path)
    output_file = open("for_tom_to_correct.jsonl", "w")
    correct_output_file = open("no_need_to_correct.jsonl", "w")
    output_docs = []
    for doc in docs:
      if doc["meta"]["doc_key"] not in id_list:
        json.dump(doc, correct_output_file)
        correct_output_file.write("\n")

    for doc_id in id_list:
        text = metadata[doc_id[:doc_id.index("_abstract")]]
        sorted_parts = find_all_docs_in_order_by_docid(docs, doc_id, text)
        for i in range(len(sorted_parts)):
            doc_part = sorted_parts[i][1]
            if not( doc_part['text'].endswith('.') or  doc_part['text'].endswith('!') or  doc_part['text'].endswith('?')) and not i == len(sorted_parts)-1:
              
                if i == len(sorted_parts)-1 :   #error case
                  import pdb; pdb.set_trace()
                              
                #checking which direction of movement results in moving less tokens
                doc_before = sorted_parts[i][1]
                doc_next = sorted_parts[i+1][1]
                
                if '.' not in doc_before and '!' not in doc_before and '?' not in doc_before:
                  extra_string_before = 10000
                else:
                  cutting_ind_from_before = doc_before['text'].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text'])) - 1])
                  extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])


                cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[0])
                extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])
                
                
                if doc_next['text'][cutting_ind_from_next-1:cutting_ind_from_next+2] == "0.0":   #edge case
                    cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[1], cutting_ind_from_next + 1)
                    extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])


                if extra_string_next >  extra_string_before: # it is better to move the previous partial sentence to next partition
                  new_before, cutting_string = correct_before_doc_removing_last_sentence(doc_before)
                  new_next = correct_next_doc_adding_first_sentence(doc_next, cutting_string)
                  
                  json.dump(new_before, correct_output_file)
                  json.dump(new_next, output_file)

                else:
                  new_next, cutting_string = correct_next_doc_removing_first_sentence(doc_next)
                  new_before = correct_before_doc_adding_last_sentence(doc_before, cutting_string)

                  json.dump(new_next, correct_output_file)
                  json.dump(new_before, output_file)

                output_file.write("\n")
                correct_output_file.write("\n")
                i+=1 # to skip the next partition that is already corrected
            else:  #the parition does not contain partial sentence and can be written to correct output
                json.dump(sorted_parts[i][1], correct_output_file)
                correct_output_file.write("\n")

                
doc_id_list = find_the_ids_with_issues("corrections/jsons/corrections_tom.jsonl")
write_stiching_docs("metadata", "corrections/jsons/corrections_tom.jsonl", doc_id_list)


