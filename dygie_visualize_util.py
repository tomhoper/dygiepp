import json
import copy
from dygie.models.shared import fields_to_batches
from collections import Counter
import numpy as np


def get_sentence_of_span(span, sentence_starts, doc_tokens):
    """
    Return the index of the sentence that the span is part of.
    """
    # Inclusive sentence ends
    sentence_ends = [x - 1 for x in sentence_starts[1:]] + [doc_tokens - 1]
    in_between = [span[0] >= start and span[1] <= end
                  for start, end in zip(sentence_starts, sentence_ends)]
    assert sum(in_between) == 1
    the_sentence = in_between.index(True)
    return the_sentence

def seen_before(element, prev_ds):
    doc_seen_flag = False
    for doc in prev_ds.js:
        if element["doc_key"] == doc["doc_key"]:
            doc_seen_flag = True
            # import pdb; pdb.set_trace()
            new_relations = element["predicted_relations"]
            for i in range(len(new_relations)):
                for j in range(len(new_relations[i])):
                  if new_relations[i][j][:5] not in doc["relations"][i]:
                    # import pdb;pdb.set_trace()
                    return False
    return doc_seen_flag

class Dataset:
    def __init__(self, json_file, pred_file=None):
        self.js = self._read(json_file, pred_file)
        self.documents = [Document(js) for js in self.js]

    def _read(self, json_file, pred_file=None):
        gold_docs = [json.loads(line) for line in open(json_file)]
        if pred_file is None:
            return gold_docs

        pred_docs = [json.loads(line) for line in open(pred_file)]
        merged_docs = []
        for gold, pred in zip(gold_docs, pred_docs):
            assert gold["doc_key"] == pred["doc_key"]
            assert gold["sentences"] == pred["sentences"]
            merged = copy.deepcopy(gold)
            for k, v in pred.items():
                if "predicted" in k:
                    merged[k] = v
            merged_docs.append(merged)

        return merged_docs

    def __getitem__(self, ix):
        return self.documents[ix]

    def __len__(self):
        return len(self.documents)

    def prune(self, count, conf_threshold, prev_ds=None):
      # to remove validation set doc keys:
      validation_doc_keylist_file = open("valid_key_list.txt")
      val_doc_key = []
      for line in validation_doc_keylist_file:
        val_doc_key.append(line[:-1])

      conf_score_list = []
      # import pdb; pdb.set_trace()
      for element in self.js:
        if prev_ds and (seen_before(element, prev_ds) or element["doc_key"] in val_doc_key):
            continue
        for j in range(len(element['predicted_relations'])):
            for i in range(len(element['predicted_relations'][j])):
              relation = element['predicted_relations'][j][i]
              if (relation[4] == "USED-FOR" or relation[4] == "scierc:USED-FOR") and float(relation[5]) >= conf_threshold:
                conf_score_list.append(relation[5])

      conf_score_list.sort(reverse=True)
      index_selected = count
      if len(conf_score_list) < count:
         index_selected = len(conf_score_list) - 1
      while(index_selected != len(conf_score_list) - 1 and conf_score_list[index_selected] == conf_score_list[index_selected+1]):
        print(index_selected)
        index_selected += 1

      while(index_selected != -1 and conf_score_list[index_selected]< conf_threshold):
        index_selected -= 1

      if index_selected == -1:
        return []
      threshold = conf_score_list[index_selected]
      print("threshold is " + str(threshold))
      pruned_elements = []
      count = 0


      for element in self.js:
        if prev_ds and seen_before(element, prev_ds):
            continue
        prune_relations = []
        avg_relation_score = 0.0
        avg_count = 0.0
        for j in range(len(element['predicted_relations'])):
            prune_relations.append([])
            for i in range(len(element['predicted_relations'][j])):
              relation = element['predicted_relations'][j][i]
              if (relation[4] == "USED-FOR" or relation[4] == "scierc:USED-FOR") and float(relation[5]) >= threshold:
                avg_relation_score += relation[5]

                prune_relations[j].append(relation[:5])
                avg_count += 1.0
        if avg_relation_score != 0.0:
          count += len(prune_relations)
          new_element = {}
          new_element["sentences"] = element["sentences"]
          new_element["doc_key"] = "covid:"+ element["doc_key"]
          # import pdb; pdb.set_trace()
          new_ner = []
          for iii in range(len(element["predicted_ner"])):
            new_row = []
            
            ner_index_seen = []
            for jjj in range(len(element["predicted_ner"][iii])):
                new_cell = []
                max_score = -1
                max_index = jjj
                span_ind = (element["predicted_ner"][iii][jjj][0], element["predicted_ner"][iii][jjj][1])
                for kkk in range(len(element["predicted_ner"][iii])):
                    if (element["predicted_ner"][iii][kkk][0], element["predicted_ner"][iii][kkk][1]) == span_ind:
                        if float(element["predicted_ner"][iii][kkk][2][0]['score']) > max_score:
                            max_score = float(element["predicted_ner"][iii][kkk][2][0]['score'])
                            max_index = kkk
                if max_index not in ner_index_seen:
                    new_cell.append(element["predicted_ner"][iii][max_index][0])
                    new_cell.append(element["predicted_ner"][iii][max_index][1])
                    new_cell.append(element["predicted_ner"][iii][max_index][2][0]['label'])
                    new_row.append(new_cell)
                    ner_index_seen.append(max_index)
            new_ner.append(new_row)
          new_element["ner"] = new_ner
          new_element["relations"] = prune_relations

          pruned_elements.append((new_element, float(avg_relation_score)/float(avg_count)))
      print (count)
      return pruned_elements


class Document:
    def __init__(self, js):
        self._doc_key = js["doc_key"]
        entries = fields_to_batches(js, ["doc_key", "clusters", "predicted_clusters", "section_starts", "dataset"])
        sentence_lengths = [len(entry["sentences"]) for entry in entries]
        sentence_starts = np.cumsum(sentence_lengths)
        sentence_starts = np.roll(sentence_starts, 1)
        sentence_starts[0] = 0
        self.sentence_starts = sentence_starts
        self.sentences = [Sentence(entry, sentence_start, sentence_ix)
                          for sentence_ix, (entry, sentence_start)
                          in enumerate(zip(entries, sentence_starts))]
        if "clusters" in js:
            self.clusters = [Cluster(entry, i, self, predicted=False)
                             for i, entry in enumerate(js["clusters"])]
        if "predicted_clusters" in js:
            self.predicted_clusters = [Cluster(entry, i, self, predicted=True)
                                       for i, entry in enumerate(js["predicted_clusters"])]

    def __repr__(self):
        return "\n".join([str(i) + ": " + " ".join(sent.text) for i, sent in enumerate(self.sentences)])

    def __getitem__(self, ix):
        return self.sentences[ix]

    def __len__(self):
        return len(self.sentences)

    def print_plaintext(self):
        for sent in self:
            print(" ".join(sent.text))


    def find_cluster(self, entity, predicted=True):
        """
        Search through coreference clusters and return the one containing the query entity, if it's
        part of a cluster. If we don't find a match, return None.
        """
        clusters = self.predicted_clusters if predicted else self.clusters
        for clust in clusters:
            for entry in clust:
                if entry.span == entity.span:
                    return clust

        return None

    @property
    def n_tokens(self):
        return sum([len(sent) for sent in self.sentences])


class Sentence:
    def __init__(self, entry, sentence_start, sentence_ix):
        self.sentence_start = sentence_start
        self.text = entry["sentences"]
        self.sentence_ix = sentence_ix
        # Gold
        if "ner_flavor" in entry:
            self.ner = [NER(this_ner, self.text, sentence_start, flavor=this_flavor)
                        for this_ner, this_flavor in zip(entry["ner"], entry["ner_flavor"])]
        elif "ner" in entry:
            self.ner = [NER(this_ner, self.text, sentence_start)
                        for this_ner in entry["ner"]]
        if "relations" in entry:
            self.relations = [Relation(this_relation, self.text, sentence_start) for
                              this_relation in entry["relations"]]
        if "events" in entry:
            self.events = Events(entry["events"], self.text, sentence_start)

        # Predicted
        if "predicted_ner" in entry:
            self.predicted_ner = [NER(this_ner, self.text, sentence_start, flavor=None) for
                                  this_ner in entry["predicted_ner"]]
        if "predicted_relations" in entry:
            self.relations = []
            for this_relation in entry["predicted_relations"]:
              # import pdb; pdb.set_trace()
              # print (float(this_relation[5]))
              # if this_relation[4] == "scierc:USED-FOR" or this_relation[4] == "USED-FOR":
                self.relations.append(Relation(this_relation, self.text, sentence_start))

        if "predicted_events" in entry:
            self.predicted_events = Events(entry["predicted_events"], self.text, sentence_start)

    def __repr__(self):
        the_text = " ".join(self.text)
        the_lengths = np.array([len(x) for x in self.text])
        tok_ixs = ""
        for i, offset in enumerate(the_lengths):
            true_offset = offset if i < 10 else offset - 1
            tok_ixs += str(i)
            tok_ixs += " " * true_offset

        return the_text + "\n" + tok_ixs

    def __len__(self):
        return len(self.text)

    def get_flavor(self, argument):
        the_ner = [x for x in self.ner if x.span == argument.span]
        if len(the_ner) > 1:
            print("Weird")
        if the_ner:
            the_flavor = the_ner[0].flavor
        else:
            the_flavor = None
        return the_flavor


class Span:
    def __init__(self, start, end, text, sentence_start):
        self.start_doc = start
        self.end_doc = end
        self.span_doc = (self.start_doc, self.end_doc)
        self.start_sent = start - sentence_start
        self.end_sent = end - sentence_start
        self.span_sent = (self.start_sent, self.end_sent)
        self.text = text[self.start_sent:self.end_sent + 1]

    def __repr__(self):
        return str((self.start_sent, self.end_sent, self.text))

    def __eq__(self, other):
        return (self.span_doc == other.span_doc and
                self.span_sent == other.span_sent and
                self.text == other.text)

    def __hash__(self):
        tup = self.span_doc + self.span_sent + (" ".join(self.text),)
        return hash(tup)


class Token:
    def __init__(self, ix, text, sentence_start):
        self.ix_doc = ix
        self.ix_sent = ix - sentence_start
        self.text = text[self.ix_sent]

    def __repr__(self):
        return str((self.ix_sent, self.text))


class Trigger:
    def __init__(self, token, label):
        self.token = token
        self.label = label

    def __repr__(self):
        return self.token.__repr__()[:-1] + ", " + self.label + ")"


class Argument:
    def __init__(self, span, role, event_type):
        self.span = span
        self.role = role
        self.event_type = event_type

    def __repr__(self):
        return self.span.__repr__()[:-1] + ", " + self.event_type + ", " + self.role + ")"

    def __eq__(self, other):
        return (self.span == other.span and
                self.role == other.role and
                self.event_type == other.event_type)

    def __hash__(self):
        return self.span.__hash__() + hash((self.role, self.event_type))


class NER:
    def __init__(self, ner, text, sentence_start, flavor=None):
        self.span = Span(ner[0], ner[1], text, sentence_start)
        self.label = ner[2]
        self.flavor = flavor

    def __repr__(self):
        return self.span.__repr__() + ": " + str(self.label)

    def __eq__(self, other):
        return (self.span == other.span and
                self.label == other.label and
                self.flavor == other.flavor)


class Relation:
    def __init__(self, relation, text, sentence_start):
        start1, end1 = relation[0], relation[1]
        start2, end2 = relation[2], relation[3]
        label = relation[4]
        if len(relation) > 6:
            score = relation[6]
        else:
            score = 1.0
        span1 = Span(start1, end1, text, sentence_start)
        span2 = Span(start2, end2, text, sentence_start)
        self.pair = (span1, span2)
        self.label = label
        self.score = score

    def __repr__(self):
        return self.pair[0].__repr__() + ", " + self.pair[1].__repr__() + ": " + self.label +  " by  score of  " + str(self.score)

    def __eq__(self, other):
        return (self.pair == other.pair) and (self.label == other.label)


class AtomicRelation:
    def __init__(self, ent0, ent1, label):
        self.ent0 = ent0
        self.ent1 = ent1
        self.label = label

    @classmethod
    def from_relation(cls, relation):
        ent0 = " ".join(relation.pair[0].text)
        ent1 = " ".join(relation.pair[1].text)
        label = relation.label
        return cls(ent0, ent1, label)

    def __repr__(self):
        return f"({self.ent0} | {self.ent1} | {self.label})"



class Event:
    def __init__(self, event, text, sentence_start):
        trig = event[0]
        args = event[1:]
        trigger_token = Token(trig[0], text, sentence_start)
        self.trigger = Trigger(trigger_token, trig[1])

        self.arguments = []
        for arg in args:
            span = Span(arg[0], arg[1], text, sentence_start)
            self.arguments.append(Argument(span, arg[2], self.trigger.label))

    def __repr__(self):
        res = "<"
        res += self.trigger.__repr__() + ":\n"
        for arg in self.arguments:
            res += 6 * " " + arg.__repr__() + ";\n"
        res = res[:-2] + ">"
        return res


class Events:
    def __init__(self, events_json, text, sentence_start):
        self.event_list = [Event(this_event, text, sentence_start) for this_event in events_json]
        self.triggers = set([event.trigger for event in self.event_list])
        self.arguments = set([arg for event in self.event_list for arg in event.arguments])

    def __len__(self):
        return len(self.event_list)

    def __getitem__(self, i):
       return self.event_list[i]

    def __repr__(self):
        return "\n\n".join([event.__repr__() for event in self.event_list])

    def span_matches(self, argument):
        return set([candidate for candidate in self.arguments
                    if candidate.span.span_sent == argument.span.span_sent])

    def event_type_matches(self, argument):
        return set([candidate for candidate in self.span_matches(argument)
                    if candidate.event_type == argument.event_type])

    def matches_except_event_type(self, argument):
        matched = [candidate for candidate in self.span_matches(argument)
                   if candidate.event_type != argument.event_type
                   and candidate.role == argument.role]
        return set(matched)

    def exact_match(self, argument):
        for candidate in self.arguments:
            if candidate == argument:
                return True
        return False


class Cluster:
    def __init__(self, cluster, cluster_id, document, predicted):
        members = []
        for entry in cluster:
            sentence_ix = get_sentence_of_span(entry, document.sentence_starts, document.n_tokens)
            sentence = document[sentence_ix]
            span = Span(entry[0], entry[1], sentence.text, sentence.sentence_start)
            # If we're doing predicted clusters, use the predicted entities.
            if predicted:
                ners = [x for x in sentence.predicted_ner if x.span == span]
            else:
                ners = [x for x in sentence.ner if x.span == span]
            assert len(ners) <= 1
            ner = ners[0] if len(ners) == 1 else None
            to_append = ClusterMember(span, ner, sentence, cluster_id)
            members.append(to_append)

        self.members = members
        self.cluster_id = cluster_id

    def __repr__(self):
        return f"{self.cluster_id}: " + self.members.__repr__()

    def __getitem__(self, ix):
        return self.members[ix]


class ClusterMember:
    def __init__(self, span, ner, sentence, cluster_id):
        self.span = span
        self.ner = ner
        self.sentence = sentence
        self.cluster_id = cluster_id

    def __repr__(self):
        return f"<{self.sentence.sentence_ix}> " + self.span.__repr__()


####################

# Code to do evaluation of predictions for a loaded dataset.

def safe_div(num, denom):
    if denom > 0:
        return num / denom
    else:
        return 0


def compute_f1(predicted, gold, matched):
    # F1 score.
    precision = safe_div(matched, predicted)
    recall = safe_div(matched, gold)
    f1 = safe_div(2 * precision * recall, precision + recall)
    return dict(precision=precision, recall=recall, f1=f1)


def evaluate_sent(sent, counts):
    # Entities.
    counts["ner_gold"] += len(sent.ner)
    counts["ner_predicted"] += len(sent.predicted_ner)
    for prediction in sent.predicted_ner:
        if any([prediction == actual for actual in sent.ner]):
            counts["ner_matched"] += 1

    # Relations.
    counts["relations_gold"] += len(sent.relations)
    counts["relations_predicted"] += len(sent.predicted_relations)
    for prediction in sent.predicted_relations:
        if any([prediction == actual for actual in sent.relations]):
            counts["relations_matched"] += 1

    # Return the updated counts.
    return counts


def evaluate_predictions(dataset):
    counts = Counter()

    for doc in dataset:
        for sent in doc:
            counts = evaluate_sent(sent, counts)

    scores_ner = compute_f1(
        counts["ner_predicted"], counts["ner_gold"], counts["ner_matched"])
    scores_relations = compute_f1(
        counts["relations_predicted"], counts["relations_gold"], counts["relations_matched"])

    return dict(ner=scores_ner, relation=scores_relations)

