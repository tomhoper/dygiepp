#the input_files should be in tsv format with these columns text, head, child, label, answer
DOC_ID  = 0
TEXT_INDEX = 1
HEAD_INDEX = 2
CHILD_INDEX = 3
LABEL_INDEX = 4
ANS_INDEX = 5

def exact_match_score(gold_rel, pred_rel, collapsed=False):
  if gold_rel[LABEL_INDEX] != pred_rel[LABEL_INDEX] and collapsed == False:
      return 0.0
  if gold_rel[HEAD_INDEX] == pred_rel[HEAD_INDEX]:
    if gold_rel[CHILD_INDEX] == pred_rel[CHILD_INDEX]:
      return 1.0
  return 0.0


def substring_match_score(gold_rel, pred_rel, collapsed=False, reversed=False):
  if gold_rel[LABEL_INDEX] != pred_rel[LABEL_INDEX] and collapsed == False:
      return 0.0
  if gold_rel[HEAD_INDEX] in pred_rel[HEAD_INDEX] or pred_rel[HEAD_INDEX] in gold_rel[HEAD_INDEX]:
    if gold_rel[CHILD_INDEX] in pred_rel[CHILD_INDEX] or pred_rel[CHILD_INDEX] in gold_rel[CHILD_INDEX]:
      return 1.0
  if reversed == True:
    if gold_rel[HEAD_INDEX] in pred_rel[CHILD_INDEX] or pred_rel[CHILD_INDEX] in gold_rel[HEAD_INDEX]:
      if gold_rel[CHILD_INDEX] in pred_rel[HEAD_INDEX] or pred_rel[HEAD_INDEX] in gold_rel[CHILD_INDEX]:
        return 1.0
  return 0.0


def refind_span(span):
  span = span.lower()
  if span.startswith('a '):
    span = span[2:]
  if span.startswith('the '):
    span = span[4:]
  span = span.replace(') ', ' ').replace('- ', ' ').replace('( ', ' ')
  return span


def partial_span_score(span1, span2):
  # import pdb; pdb.set_trace()
  span1_tokens = refind_span(span1).split(' ')
  span2_tokens = refind_span(span2).split(' ')

  if len(span1_tokens) > len(span2_tokens):
      max_length = len(span1_tokens)
  else:
      max_length = len(span2_tokens)
  common = [x for x in span1_tokens if x in span2_tokens]
  all_words = [x for x in span1_tokens]
  for word in span2_tokens:
    all_words.append(word)

  # import pdb; pdb.set_trace()
  return float(len(common)/max_length)
  # return float(len(set(common))/len(set(all_words)))

def partial_match_score(gold_rel, pred_rel, collapsed=False):
  if gold_rel[LABEL_INDEX] != pred_rel[LABEL_INDEX] and collapsed == False:
      return 0.0
  if partial_span_score(gold_rel[HEAD_INDEX], pred_rel[HEAD_INDEX]) >= 0.3:
    if partial_span_score(gold_rel[CHILD_INDEX], pred_rel[CHILD_INDEX]) >= 0.3:
      return 1.0
  return 0.0


def scierc_partial_match_score(gold_rel, pred_rel, collapsed=False):
  if gold_rel[LABEL_INDEX] != pred_rel[LABEL_INDEX] and collapsed == False:
      return 0.0
  if refind_span(gold_rel[HEAD_INDEX]).split(' ')[0] ==  refind_span(pred_rel[HEAD_INDEX]).split(' ')[0]:
    if refind_span(gold_rel[CHILD_INDEX]).split(' ')[0] ==  refind_span(pred_rel[CHILD_INDEX]).split(' ')[0]:
      return 1.0
  return 0.0


def eval_accept_reject(gold_data, pred_data):
  gold_text = [x[TEXT_INDEX] for x in gold_data]
  pred_text = [x[TEXT_INDEX] for x in pred_data]
  common_count = 0.0
  
  seen_text = []
  for data in gold_data:
    if data[TEXT_INDEX] in pred_text and data[TEXT_INDEX] not in seen_text:
      common_count += 1.0
      seen_text.append(data[TEXT_INDEX])
  for data in pred_data:
    if data[TEXT_INDEX] in gold_text and data[TEXT_INDEX] not in seen_text:
      common_count += 1.0
      seen_text.append(data[TEXT_INDEX])
  correct_count= 0.0
  
  seen_text = []
  for rel_info in gold_data:
      gold_text = rel_info[TEXT_INDEX]
      for pred_rel_info in pred_data:
        if pred_rel_info[TEXT_INDEX] == gold_text:
          if pred_rel_info[ANS_INDEX] == rel_info[ANS_INDEX] and pred_rel_info[TEXT_INDEX] not in seen_text :
            seen_text.append(pred_rel_info[TEXT_INDEX])
            correct_count += 1.0
  print("accept reject agreement is :" + str(correct_count/common_count))

def eval_annotation_qualilty(gold_data, pred_data):
  
  exact_match_correct_count = 0.0
  partial_match_correct_count = 0.0
  
  #collapsed ==> no checking relations
  exact_match_collapsed_correct_count = 0.0
  partial_match_collapsed_correct_count = 0.0

  scierc_partial_match_correct_count = 0.0
  scierc_partial_match_collapse_correct_count = 0.0


  substring_match_correct_count = 0.0
  substring_match_collapse_score = 0.0
  
  common_count = 0.0
  
  gold_text = [x[TEXT_INDEX] for x in gold_data]
  pred_text = [x[TEXT_INDEX] for x in pred_data]
  
  for data in gold_data:
    if data[TEXT_INDEX] in pred_text:
      common_count += 1.0
  for data in pred_data:
    if data[TEXT_INDEX] in gold_text:
      common_count += 1.0

  for rel_info in gold_data:
      gold_text = rel_info[TEXT_INDEX]
      for pred_rel_info in pred_data:
        if pred_rel_info[TEXT_INDEX] == gold_text:
            # print(gold_text)
            exact_match_correct_count += exact_match_score(rel_info, pred_rel_info)
            partial_match_correct_count += partial_match_score(rel_info, pred_rel_info)
            scierc_partial_match_correct_count += scierc_partial_match_score(rel_info, pred_rel_info)
            substring_match_correct_count += substring_match_score(rel_info, pred_rel_info)
            exact_match_collapsed_correct_count += exact_match_score(rel_info, pred_rel_info, collapsed=True)
            partial_match_collapsed_correct_count += partial_match_score(rel_info, pred_rel_info, collapsed=True)
            scierc_partial_match_collapse_correct_count += scierc_partial_match_score(rel_info, pred_rel_info, collapsed=True)
            substring_match_collapse_score += substring_match_score(rel_info, pred_rel_info, collapsed=True)
  
  # print(common_count)
  score_partial = 2 *partial_match_correct_count / common_count
  score_partial_collapse = 2 * partial_match_collapsed_correct_count / common_count

  score_scierc_partial = 2 *scierc_partial_match_correct_count / common_count
  score_scierc_partial_collapse = 2 * scierc_partial_match_collapse_correct_count / common_count

  score_substring_match = 2 *substring_match_correct_count / common_count
  score_substring_match_collapse_score = 2 * substring_match_collapse_score / common_count


  print("partial_score >=0.3 NON collapse is " +  str(score_partial) + '  substring match partial score is ' + str(score_substring_match))
  print("partial_score >=0.3 collapse is " +  str(score_partial_collapse) + '  substring match partial score is ' + str(score_substring_match_collapse_score))

############################################################################
def eval_relation_qualilty(gold_data, pred_data):
  
  gold_ids = [x[DOC_ID] for x in gold_data]
  pred_relations = []
  for rel in pred_data:
    pair = (rel[HEAD_INDEX], rel[CHILD_INDEX])
    if pair in pred_data:
      print("pair already in predictions :" + str(pair))
    if pair not in pred_relations:
      pred_relations.append(pair)

  gold_relations = []
  for rel in gold_data:
    if 'used' not in rel[LABEL_INDEX]:
      continue
    pair = (rel[HEAD_INDEX], rel[CHILD_INDEX])
    if pair == ('', ''):
      continue
    if pair in gold_relations:
      print("pair in gold " + str(pair))
    if pair not in gold_relations:
      gold_relations.append(pair)


  pairs_find = []
  for rel_info in gold_data:
      if rel_info[ANS_INDEX] != "accept":
        continue
      gold_text = rel_info[TEXT_INDEX]
      for pred_rel_info in pred_data:

          if pred_rel_info[DOC_ID] != rel_info[DOC_ID]:
            continue
          if substring_match_score(rel_info, pred_rel_info, collapsed=True, reversed=True)> 0.0:
            pair = (rel_info[HEAD_INDEX], rel_info[CHILD_INDEX], pred_rel_info[HEAD_INDEX], pred_rel_info[CHILD_INDEX])

            if pair not in pairs_find:
              pairs_find.append(pair)
            
  
  partial_match_correct_count = float(len(pairs_find))
  partial_match_precision = float(partial_match_correct_count/len(pred_relations))
  partial_match_recal = float(partial_match_correct_count/len(gold_relations))
  if partial_match_precision != 0:
    partial_match_f1 = 2*(partial_match_precision*partial_match_recal)/(partial_match_recal+ partial_match_precision)
  else:
    partial_match_f1 = 0
  # import pdb; pdb.set_trace()
  
  print("Considering partial match NOT collapsed : precision is " + str(partial_match_precision) + " recal is " + str(partial_match_recal) + " f1 is " + str(partial_match_f1))

def read_file(file_name):
  data_list = []
  input_file = open(file_name)
  for line in input_file:
      line_parts = line[:-1].lower().split("\t")
      if line_parts[ANS_INDEX] != "ignore":
        # import pdb; pdb.set_trace()
        data_list.append(line_parts)
  return data_list


def agreement_procedure():
  madeline_data = read_file("madeline_annotations.tsv")
  kristina_data = read_file("kristina_annotations.tsv")
  arezou_data = read_file("arezou_annotations.tsv")
  jeff_data = read_file("jeff_annotations.tsv")
  megan_data = read_file("megan_annotations.tsv")
  print("annotators madeline, arezou: ")
  eval_annotation_qualilty(madeline_data, arezou_data)
  print(" ")

  print("annotator madeline, kristina: ")
  eval_annotation_qualilty(madeline_data, kristina_data)
  print(" ")

  print("annotator madeline, megan: ")
  eval_annotation_qualilty(madeline_data, megan_data)
  print(" ")

  print("annotator madeline, jeff: ")
  eval_annotation_qualilty(madeline_data, jeff_data)
  print(" ")


def eval_procedure():
  bio_iter0 = read_file("bioDygie_validation_iter0.tsv")
  madeline_data = read_file("madeline_annotations.tsv")
  bio_iter0 = read_file("bioDygie_validation_iter0.tsv")
  bio_iter1 = read_file("bioDygie_validation_iter1.tsv")
  iter0 = read_file("Dygie_validation_iter0.tsv")
  iter1 = read_file("Dygie_validation_iter1.tsv")
  bio_join = read_file("bio_dygie_join_iters.tsv")
  join = read_file("dygie_join_iters.tsv")
  print("iter 0: dygie :")
  eval_relation_qualilty(madeline_data, iter0)
  print(" ")
  print("iter 1: dygie :")
  eval_relation_qualilty(madeline_data, iter1)
  print(" ")
  print("iter 0: bio_dygie :")
  eval_relation_qualilty(madeline_data, bio_iter0)
  print(" ")
  print("iter 1: bio_dygie :")
  eval_relation_qualilty(madeline_data, bio_iter1)
  print(" ")
  print("joined: bio_dygie :")
  eval_relation_qualilty(madeline_data, bio_join)
  print(" ")
  print("joined: dygie :")
  eval_relation_qualilty(madeline_data, join)
  # print(" ")

agreement_procedure()
