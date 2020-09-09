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
        if not( doc['text'].rstrip().endswith('.') or  doc['text'].rstrip().endswith('!') or  doc['text'].rstrip().endswith('?')):
          if doc['meta']['doc_key'] not in doc_id_list:
            doc_id_list.append(doc['meta']['doc_key'])
    # print((doc_id_list))
    return doc_id_list

def find_all_docs_in_order_by_docid(docs, doc_id, text):
  selected_docs = []
  seen_starts = []
  
  for doc in docs:
    if doc['meta']['doc_key'] == doc_id:
      # if doc_id == "ke0tkpso_abstract":
      #     import pdb; pdb.set_trace()
      text_start_ind = text.index(doc["text"])
      if text_start_ind not in seen_starts:
        selected_docs.append([text_start_ind, doc])
        seen_starts.append(text_start_ind)

  sorted_docs = sorted(selected_docs,key=itemgetter(0),reverse=False)
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

    
    while (len(doc["text"]) > cutting_ind+1 and doc['text'][cutting_ind+1].isdigit()) or doc['text'][cutting_ind-8:cutting_ind+1] == "D61 in E." or (len(doc['text']) > cutting_ind+3 and (doc['text'][cutting_ind-3] == '.' or doc['text'][cutting_ind+3] == '.')):         
    # if doc['text'][cutting_ind-1:cutting_ind+2] in ["9.1" , "0.0"]:   #edge case
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

    res = ut.convert_to_json(res["text"].strip(), relation_pairs, res["meta"]["doc_key"])
    res["answer"] = doc["answer"]
    return res, extra_string

def correct_next_doc_adding_first_sentence(doc, extra_string):
    
    res = deepcopy(doc)
    if "answer" not in doc:
      import pdb; pdb.set_trace()
    try:
      res["text"] = extra_string.strip() + ' ' + doc['text']
    except:
      import pdb; pdb.set_trace()
    
    relation_pairs = []
    for rel in res["relations"]:
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"].strip(), relation_pairs, res["meta"]["doc_key"])

    res["answer"] = doc["answer"]
    return res

def correct_before_doc_adding_last_sentence(doc, extra_string):
    
    res = deepcopy(doc)
    res["text"] =  doc['text'].strip() + ' ' + extra_string.strip()
    
    
    relation_pairs = []
    for rel in res["relations"]:
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"].strip(), relation_pairs, res["meta"]["doc_key"])
    res["answer"] = doc["answer"]
    return res

def correct_before_doc_removing_last_sentence(doc):
    
    res = deepcopy(doc)
    try:
      cutting_ind = doc['text'].rindex(re.findall("\?|\.|\!", doc['text'])[len(re.findall("\?|\.|\!", doc['text'])) - 1])
      extra_string = doc['text'][cutting_ind+1:]
    except:
      import pdb; pdb.set_trace()

    while doc['text'][cutting_ind+1].isdigit() or doc['text'][cutting_ind-8:cutting_ind+1] == "D61 in E." or (len(doc['text']) > cutting_ind+3 and (doc['text'][cutting_ind-3] == '.' or doc['text'][cutting_ind+3] == '.')):
      try:
        cutting_ind = doc['text'][:cutting_ind-1].rindex(re.findall("\?|\.|\!", doc['text'])[len(re.findall("\?|\.|\!", doc['text']))-2])
        extra_string = doc['text'][cutting_ind+1:]
      except:
        cutting_ind = -1
        extra_string = doc['text']
        break

          # cutting_ind = doc['text'][:cutting_ind-1].rindex(re.findall("\?|\.|\!", doc['text'])[len(re.findall("\?|\.|\!", doc['text']))-2])
          # extra_string = doc['text'][cutting_ind+1:]


    
    res["text"] = doc['text'][:cutting_ind+1]
    
    relation_pairs = []
    for rel in res["relations"]:
        if rel['head_span']["end"] > len(res["text"]) or rel['child_span']["end"] > len(res["text"]):
          continue
        head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
        child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
        relation_pairs.append([rel['label'], head, child])

    res = ut.convert_to_json(res["text"].strip(), relation_pairs, res["meta"]["doc_key"])
    res["answer"] = doc["answer"]
    return res, extra_string



def add_missing_parts(text, sorted_list, doc_key):
    # if doc_key == "ld0vo1rl_abstract":
    #   import pdb; pdb.set_trace()
    # if doc_id == "ke0tkpso_abstract":
    #           import pdb; pdb.set_trace()
    new_sorted_list = []
    if sorted_list[0][0] != 0: # first partition is missing
      part_text = text[:sorted_list[0][0]]

      new_part = ut.convert_to_json(part_text, [], doc_key)
      new_part['answer'] = "reject"
      new_sorted_list.append([0, new_part])

    else:
      new_sorted_list.append(sorted_list[0])

    for ind in range(1, len(sorted_list)):
      if abs(sorted_list[ind][0] - new_sorted_list[len(new_sorted_list)-1][0] - len(new_sorted_list[len(new_sorted_list)-1][1]['text'])) < 2:
        new_sorted_list.append(sorted_list[ind])
      else:
        ls_ind = new_sorted_list[len(new_sorted_list)-1][0] + len(new_sorted_list[len(new_sorted_list)-1][1]['text'])
        cur_ind = sorted_list[ind][0]
        part_text = text[ls_ind:cur_ind]
        new_part = ut.convert_to_json(part_text, [], doc_key)
        new_part['answer'] = 'reject'
        new_sorted_list.append([ls_ind, new_part])
        new_sorted_list.append(sorted_list[ind])
    if new_sorted_list[len(new_sorted_list)-1][0] + len(new_sorted_list[len(new_sorted_list)-1][1]['text']) < len(text)-1:
        ls_ind = new_sorted_list[len(new_sorted_list)-1][0] + len(new_sorted_list[len(new_sorted_list)-1][1]['text'])
        part_text = text[ls_ind:]
        new_part = ut.convert_to_json(part_text, [], doc_key)
        new_part['answer'] = 'reject'
        new_sorted_list.append([ls_ind, new_part])

    return new_sorted_list
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




def write_stiching_docs(metadata_path, input_file_path, id_list, stiching_file_path, correct_file_path):
    docs = [json.loads(line) for line in open(input_file_path)]
    metadata = read_metadata(metadata_path)
    output_file = open(stiching_file_path, "w")
    correct_output_file = open(correct_file_path, "w")

    output_docs = []
    for doc in docs:
      if doc["meta"]["doc_key"] not in id_list:
        json.dump(doc, correct_output_file)
        correct_output_file.write("\n")

    for doc_id in id_list:
        text = metadata[doc_id[:doc_id.index("_abstract")]]
        text = " ".join(process_paragraph(text)[0])
        sorted_parts = find_all_docs_in_order_by_docid(docs, doc_id, text)
        
        sorted_parts = add_missing_parts(text, sorted_parts, doc_id)
        next_need_stiching = False
        new_next_flag = False
        for i in range(len(sorted_parts)):
            # if doc_id == "tc14sa65_abstract":
            #     import pdb; pdb.set_trace()
            
            if new_next_flag == True:
              new_next_flag = False
              continue
            doc_part = sorted_parts[i][1]
            if not( doc_part['text'].rstrip().endswith('.') or  doc_part['text'].rstrip().endswith('!') or  doc_part['text'].rstrip().endswith('?')) and not i == len(sorted_parts)-1:
                             
                #checking which direction of movement results in moving less tokens
                doc_before = sorted_parts[i][1]
                doc_next = sorted_parts[i+1][1]
                
                if '.' not in doc_before['text'] and '!' not in doc_before['text'] and '?' not in doc_before['text']:
                  extra_string_before = 10000
                else:
                  cutting_ind_from_before = doc_before['text'].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text'])) - 1])
                  extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])

                  while doc_before['text'][cutting_ind_from_before+1].isdigit() or doc_before['text'][cutting_ind_from_before-8:cutting_ind_from_before+1] == "D61 in E." or (len(doc_before['text']) > cutting_ind_from_before+3 and (doc_before['text'][cutting_ind_from_before-3] == '.' or doc_before['text'][cutting_ind_from_before+3] == '.')):
                    try:
                      cutting_ind_from_before = doc_before['text'][:cutting_ind_from_before-1].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text']))-2])
                      extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])
                      if (len(doc_before['text']) > cutting_ind_from_before+4 and doc_before['text'][cutting_ind_from_before+3] == '.'):               
                        cutting_ind_from_before = doc_before['text'][:cutting_ind_from_before-1].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text']))-3])
                        extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])
                    except:
                      extra_string_before = 10000
                      break
  
                try:
                  cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[0])
                  extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])
                  
                except:
                  extra_string_next = 5000000
                  # import pdb; pdb.set_trace()
                
                while (cutting_ind_from_next+1 < len(doc_next['text']) and doc_next['text'][cutting_ind_from_next+1].isdigit()) or doc_next['text'][cutting_ind_from_next-8:cutting_ind_from_next+1] == "D61 in E." or (len(doc_next['text']) > cutting_ind_from_next+3 and (doc_next['text'][cutting_ind_from_next-3] == '.' or doc_next['text'][cutting_ind_from_next+3] == '.')):
                # if doc_next['text'][cutting_ind_from_next-1:cutting_ind_from_next+2] in ["9.1","0.0"]:   #edge case
                  try:  
                    cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[1], cutting_ind_from_next + 1)
                    extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])
                  except:
                    extra_string_next = 5000000
                    break
                    # import pdb; pdb.set_trace()

                
                if extra_string_next >  extra_string_before: # it is better to move the previous partial sentence to next partition
                  if doc_before['text'] == "":
                    import pdb; pdb.set_trace()
                  new_before, cutting_string = correct_before_doc_removing_last_sentence(doc_before)
                  new_next = correct_next_doc_adding_first_sentence(doc_next, cutting_string)
                  if new_next['text'] == "":
                    import pdb; pdb.set_trace()

                  else:
                    if "answer" not in new_before:
                      import pdb; pdb.set_trace()
                    json.dump(new_before, correct_output_file)
                    correct_output_file.write("\n")
                    next_need_stiching = True

                else:
                  new_next, cutting_string = correct_next_doc_removing_first_sentence(doc_next)
                  new_before = correct_before_doc_adding_last_sentence(doc_before, cutting_string)


                  json.dump(new_before, output_file)
                  output_file.write("\n")

                if new_next['text'] != "":
                  sorted_parts[i+1][1] = new_next
                else:
                  new_next_flag = True
            else:  #the parition does not contain partial sentence and can be written to correct output
                if next_need_stiching == True:
                  next_need_stiching = False
                  json.dump(sorted_parts[i][1], output_file)
                  output_file.write("\n")
                else:
                  json.dump(sorted_parts[i][1], correct_output_file)
                  correct_output_file.write("\n")




def write_stiching_docs_events(metadata_path, input_file_path, id_list, stiching_file_path, correct_file_path):
    docs = [json.loads(line) for line in open(input_file_path)]
    # metadata = read_metadata(metadata_path)
    output_file = open(stiching_file_path, "w")
    correct_output_file = open(correct_file_path, "w")

    output_docs = []
    for doc in docs:
      if doc["meta"]["doc_key"] not in id_list:
        json.dump(doc, correct_output_file)
        correct_output_file.write("\n")

    for doc_id in id_list:
        # text = metadata[doc_id[:doc_id.index("_abstract")]]
        text = " ".join(process_paragraph(text)[0])
        sorted_parts = find_all_docs_in_order_by_docid(docs, doc_id, text)
        
        sorted_parts = add_missing_parts(text, sorted_parts, doc_id)
        next_need_stiching = False
        new_next_flag = False
        for i in range(len(sorted_parts)):
            # if doc_id == "tc14sa65_abstract":
            #     import pdb; pdb.set_trace()
            
            if new_next_flag == True:
              new_next_flag = False
              continue
            doc_part = sorted_parts[i][1]
            if not( doc_part['text'].rstrip().endswith('.') or  doc_part['text'].rstrip().endswith('!') or  doc_part['text'].rstrip().endswith('?')) and not i == len(sorted_parts)-1:
                             
                #checking which direction of movement results in moving less tokens
                doc_before = sorted_parts[i][1]
                doc_next = sorted_parts[i+1][1]
                
                if '.' not in doc_before['text'] and '!' not in doc_before['text'] and '?' not in doc_before['text']:
                  extra_string_before = 10000
                else:
                  cutting_ind_from_before = doc_before['text'].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text'])) - 1])
                  extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])

                  while doc_before['text'][cutting_ind_from_before+1].isdigit() or doc_before['text'][cutting_ind_from_before-8:cutting_ind_from_before+1] == "D61 in E." or (len(doc_before['text']) > cutting_ind_from_before+3 and (doc_before['text'][cutting_ind_from_before-3] == '.' or doc_before['text'][cutting_ind_from_before+3] == '.')):
                    try:
                      cutting_ind_from_before = doc_before['text'][:cutting_ind_from_before-1].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text']))-2])
                      extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])
                      if (len(doc_before['text']) > cutting_ind_from_before+4 and doc_before['text'][cutting_ind_from_before+3] == '.'):               
                        cutting_ind_from_before = doc_before['text'][:cutting_ind_from_before-1].rindex(re.findall("\?|\.|\!", doc_before['text'])[len(re.findall("\?|\.|\!", doc_before['text']))-3])
                        extra_string_before = len(doc_before['text'][cutting_ind_from_before+1:])
                    except:
                      extra_string_before = 10000
                      break
  
                try:
                  cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[0])
                  extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])
                  
                except:
                  extra_string_next = 5000000
                  # import pdb; pdb.set_trace()
                
                while (cutting_ind_from_next+1 < len(doc_next['text']) and doc_next['text'][cutting_ind_from_next+1].isdigit()) or doc_next['text'][cutting_ind_from_next-8:cutting_ind_from_next+1] == "D61 in E." or (len(doc_next['text']) > cutting_ind_from_next+3 and (doc_next['text'][cutting_ind_from_next-3] == '.' or doc_next['text'][cutting_ind_from_next+3] == '.')):
                # if doc_next['text'][cutting_ind_from_next-1:cutting_ind_from_next+2] in ["9.1","0.0"]:   #edge case
                  try:  
                    cutting_ind_from_next = doc_next['text'].index(re.findall("\?|\.|\!", doc_next['text'])[1], cutting_ind_from_next + 1)
                    extra_string_next = len(doc_next['text'][:cutting_ind_from_next+1])
                  except:
                    extra_string_next = 5000000
                    break
                    # import pdb; pdb.set_trace()

                
                if extra_string_next >  extra_string_before: # it is better to move the previous partial sentence to next partition
                  if doc_before['text'] == "":
                    import pdb; pdb.set_trace()
                  new_before, cutting_string = correct_before_doc_removing_last_sentence(doc_before)
                  new_next = correct_next_doc_adding_first_sentence(doc_next, cutting_string)
                  if new_next['text'] == "":
                    import pdb; pdb.set_trace()

                  else:
                    if "answer" not in new_before:
                      import pdb; pdb.set_trace()
                    json.dump(new_before, correct_output_file)
                    correct_output_file.write("\n")
                    next_need_stiching = True

                else:
                  new_next, cutting_string = correct_next_doc_removing_first_sentence(doc_next)
                  new_before = correct_before_doc_adding_last_sentence(doc_before, cutting_string)


                  json.dump(new_before, output_file)
                  output_file.write("\n")

                if new_next['text'] != "":
                  sorted_parts[i+1][1] = new_next
                else:
                  new_next_flag = True
            else:  #the parition does not contain partial sentence and can be written to correct output
                if next_need_stiching == True:
                  next_need_stiching = False
                  json.dump(sorted_parts[i][1], output_file)
                  output_file.write("\n")
                else:
                  json.dump(sorted_parts[i][1], correct_output_file)
                  correct_output_file.write("\n")

                

# doc_id_list = find_the_ids_with_issues("corrections/jsons/corrections_tom.jsonl")
# write_stiching_docs("metadata", "corrections/jsons/corrections_tom.jsonl", doc_id_list)



