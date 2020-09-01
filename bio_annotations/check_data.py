import json

tom_annotations = [json.loads(line) for line in open("no_need_to_correct.jsonl")]
madeline_annotations = [json.loads(line) for line in open("validations/madeline_final_corrected.jsonl")]
tom_text = [] 
for item in tom_annotations:
    if item["answer"] == "accept":
      tom_text.append(item["text"])

madeline_text = [] 
for item in madeline_annotations:
    if item["answer"] == "accept":
      madeline_text.append(item["text"])

count_tom = 0 
for text in tom_text:
  if text not in madeline_text:
    # import pdb; pdb.set_trace()
    print("for tom this is not there ::: "  + text)
    count_tom += 1

output_file = open("diff.jsonl", "w")

count_madeline = 0 
for item in madeline_annotations:
  if item["text"] not in tom_text and item["answer"] == "accept":
    # import pdb; pdb.set_trace()
    json.dump(item, output_file)
    output_file.write("\n")
    print("for madeline this is not there ::: "  + text)

    count_madeline += 1

print(count_tom)
print(count_madeline)
