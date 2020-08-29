import json

def find_cross_sentence_rel_stats(input_filepath): #the input_file is the original jsonl file from the annotations.
    cross_sentence_relation_count = 0
    total_relation_count = 0
    docs = [json.loads(line) for line in open(input_filepath)]
    for doc in docs:
        text = doc["text"]
        sentences = text.replace('?',",").replace('|',",").split('. ')
        total_relation_count += len(doc["relations"])
        for rel in doc["relations"]:
            head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
            
            child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
            not_seen_in_same_sentence = True
            for sent in sentences:
              if head in sent and child in sent:
                not_seen_in_same_sentence = False
                break
            if not_seen_in_same_sentence:
                cross_sentence_relation_count += 1
    print("out of " + str(total_relation_count) + " the number of cross sentence relations is : " + str(cross_sentence_relation_count))


def create_sentence_level_relations_tsv(input_filepath):
    output_tsv_file = open("sentence_level_complete.tsv", "w")
    docs = [json.loads(line) for line in open(input_filepath)]
    for doc in docs:
        text = doc["text"]
        doc_key = doc['meta']['doc_key']
        answer = doc['answer']
        annotator_name = "tom"
        if answer == "reject" or answer == "ignore":
          continue
        sentences = text.replace('?',",").replace('|',",").split('. ')

        for rel in doc["relations"]:
            head = doc['text'][rel['head_span']["start"]:rel['head_span']["end"]]
            child = doc['text'][rel['child_span']["start"]:rel['child_span']["end"]]
            relation_label = rel['label']

            if len(text)-1 > rel['head_span']["end"] and (text[rel['head_span']["end"]]) != " ":
              end_index = text.index(" ", rel['head_span']['end'])
              head = text[rel['head_span']['start']:end_index]
              if head[len(head)-1] == '.' or head[len(head)-1] == '?' or head[len(head)-1] == '!':
                head = head[:-1]

            if len(text)-1 > rel['child_span']["end"] and (text[rel['child_span']["end"]]) != " ":
              end_index = text.index(" ", rel['child_span']['end'])
              child = text[rel['child_span']['start']:end_index]
              if child[len(child)-1] == '.' or child[len(child)-1] == '?' or child[len(child)-1] == '!':
                child = child[:-1]

            for sent in sentences:
              if head in sent and child in sent:
                output_tsv_file.write(doc_key + '\t' + sent + '\t' + head + '\t' + child + '\t' + relation_label + '\taccept\t' + annotator_name + '\n')
                
                
create_sentence_level_relations_tsv("tom_output_total.jsonl")
