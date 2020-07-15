import allennlp_models.syntax.srl
from allennlp.predictors.predictor import Predictor
import pandas as pd
import re
import itertools
import scispacy
import spacy
import numpy as np
import copy
from collections import defaultdict
spacy_nlp = spacy.load('en_core_web_sm')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
nlp = spacy.load("en_core_sci_sm")
from rouge import Rouge 
rouge = Rouge()

def get_openie_predictor():
    openiepredictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/openie-model.2020.03.26.tar.gz")
    return(openiepredictor)

def get_srl_predictor():
    import allennlp_models.syntax.srl
    srlpredictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz")
    return(srlpredictor)

def allenlp_base_relations(predictor,eval_df):
    uniquetext = eval_df.drop_duplicates(subset=["text"])
    print("getting predictions...")
    d = [{"sentence":t} for t in uniquetext.text.values]
    preds = predictor.predict_batch_json(d)

    relations =[]
    i = 0
    for sent_pred in preds:
        for v in sent_pred["verbs"]:
            rels = re.findall('\[([^]]+)', v["description"])
            relsv = [r.lstrip("V:") for r in rels if r.startswith("V")]
            rels0 = [r.lstrip("ARG0:") for r in rels if r.startswith("ARG0")]
            rels1 = [r.lstrip("ARG1:") for r in rels if r.startswith("ARG1")]
            if len(relsv) and len(rels0) and len(rels1):
                relations.append([uniquetext.iloc[i]["id"],rels0[0],rels1[0]])
        i+=1
    return relations

def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return len(s1.intersection(s2)) / len(s1.union(s2))

def filter_stopwords(tokens):
    return " ".join([t for t in tokens if t.lower() not in spacy_stopwords])


def span_matching(span1,span2,metric,thresh=None):
    match = False
    if metric =="substring":
        if span1 in span2 or span2 in span1:
            return True
    elif metric =="jaccard":
        j = jaccard_similarity(span1.split(),span2.split())
        if j>thresh:
            return True
    elif metric =="head":
        doc = nlp(span1)
        root1 = [t.text for t in doc if t.dep_ =="ROOT"]
        doc = nlp(span2)
        root2 = [t.text for t in doc if t.dep_ =="ROOT"]
        if root1[0] == root2[0]:
            return True
    elif metric =="rouge":
        raise NotImplementedError
    return match

def relation_matching(pair,metric,labels=[1,1],thresh=0.5,filter_stop=False,span_mode = False):
      match = False
      arg0match = False
      arg1match = False
      p1 = pair[0]
      p2 = pair[1]
      if metric=="head":
          filter_stop = False
      if filter_stop:
        p1 = [filter_stopwords(p1[0].split()),filter_stopwords(p1[1].split())]
        p2 = [filter_stopwords(p2[0].split()),filter_stopwords(p2[1].split())]

      if span_matching(p1[0],p2[0],metric,thresh):
          arg0match = True
          if span_matching(p1[1],p2[1],metric,thresh):
              arg1match = True
              if labels[0]==labels[1]:
                match=True
      if span_mode:
          return (arg0match or arg1match) and labels[0]==labels[1]
      return match

def allpairs_base(golddf,pair_type="NNP"):
    print("loading scispacy model for dep parse and NER...")
    #https://github.com/allenai/scispacy#available-models
    nlp = spacy.load("en_core_sci_sm")

    abstract2np = defaultdict(list)
    for row in golddf.drop_duplicates(subset=["id","text"]).iterrows():
        doc = nlp(row[1].text)
        for sent in doc.sents:
            if pair_type=="NNP":
                spans = [nnp.text for nnp in sent.noun_chunks]
            elif pair_type=="NER":
                spans = [ent.text for ent in sent.ents]
            elif pair_type=="joint":
                spans = [nnp.text for nnp in sent.noun_chunks] + [ent.text for ent in sent.ents]
            nnp_pairs = list(itertools.combinations(spans,2)) + list(itertools.combinations(spans[::-1],2))
            abstract2np[row[1].id]+=nnp_pairs

    relations = []
    for k,v in abstract2np.items():
        _=[relations.append((k,m[0],m[1])) for m in v]
    return relations

def depparse_base(golddf,pair_type="NNP"):
    relations = []
    print("loading scispacy model for dep parse and NER...")
    #https://github.com/allenai/scispacy#available-models


    uniquetext = golddf.drop_duplicates(subset=["id","text"])
    for row in uniquetext.iterrows():
        doc = nlp(row[1].text)
        
        if pair_type=="NNP":
            nps = list(doc.noun_chunks)
        elif pair_type=="NER":
            nps = list(doc.ent)

        nps = [n for n in nps if not n.root.is_stop]
        for e in nps:
            subject = None
            if e.root.dep_ in ("dobj","pobj"):
                subject = [w for w in e.root.head.lefts if w.dep_ in ["nsubj"]]
                subject = [s.text for s in subject if not s.is_stop]
                if len(subject):
                    subject = " ".join([s for s in subject])
                    matches = [subject in n.text for n in nps]
                    if len(matches):
                        matches = np.array(nps)[np.where(matches)[0]]
                        matches = [item for sublist in matches for item in sublist]
                        if len(matches):
                            _=[relations.append((row[1]["id"],m.text, e.text)) for m in matches]
            if e.root.dep_ in ("nsubj"):
                subject = [w for w in e.root.head.rights if w.dep_ in ["dobj","pobj"]]
                if subject:
                    #
                    subject = [s.text for s in subject if not s.is_stop]
                    if len(subject):
                        subject = " ".join([s for s in subject])
                        matches = [subject in n.text for n in nps]
                        if len(matches):
                            matches = np.array(nps)[np.where(matches)[0]]
                            matches = [item for sublist in matches for item in sublist]
                            if len(matches):
                                _=[relations.append((row[1]["id"],m.text, e.text)) for m in matches]
    return relations


def find_transivity_relations(rels):
    new_added = True
    seen_new = []
    while new_added:
        new_list = [x for x in rels.iterrows()]
        new_added = False
        print(len([x for x in rels.iterrows()]))
        for row1 in new_list:
            for row2 in new_list:
                if (row1[0] != row2[0]):  #we want to find transivity within same document
                    continue
                if row1[1].equals(row2[1]):
                    continue
                if row1[1]['arg1'] == row2[1]['arg0'] and (row1[1]['arg0'], row2[1]['arg1']) not in seen_new:
                  new_data = {'id': [row1[0] + ''] , 
                              'arg0': [row1[1]['arg0']],
                              'arg1': [row2[1]['arg1']]
                              }

                  if "rel" in rels.columns:
                    new_data['rel']: [row1[1]['rel']]
                  if "conf" in rels.columns:
                    new_data['conf']: [row1[1]['conf'] * row2[1]['conf']]
                  
                  seen_new.append((row1[1]['arg0'], row2[1]['arg1']))
                  df = pd.DataFrame(new_data).set_index("id",inplace=False)
                  rels = rels.append(df)
                  new_added = True

    return rels

def ie_eval(relations,golddf,collapse = False, match_metric="substring",jaccard_thresh=0.5, transivity=True):
    # import pdb; pdb.set_trace()
    goldrels = golddf[["id","arg0","arg1","rel"]]#.drop_duplicates()
    goldrels = goldrels.drop_duplicates(subset =["id","arg0","arg1"]).set_index("id")
    
    if transivity:
        goldrels = find_transivity_relations(goldrels)

    #only get rel for our model / gold, otherwise assume one collapsed label
    if "conf" in relations.columns:
        predrels = relations[["id","arg0","arg1","rel","conf"]].set_index("id",inplace=False)
    else:
        predrels = relations[["id","arg0","arg1"]].set_index("id",inplace=False)

    good_preds = []
    seen_pred_gold = {}
    for i in predrels.index.unique():
        if i in goldrels.index.unique():
            gold = goldrels.loc[i]
            if type(predrels.loc[i]) == pd.core.series.Series:
                preds = [predrels.loc[i].values]
            else:
                preds = predrels.loc[i].values
            c = list(itertools.product(gold.values, preds))
            for pair in c:
                if collapse:
                    labels = [1,1]
                else:
                    labels = [pair[0][2],pair[1][2]]
                m = relation_matching(pair,metric=match_metric, labels = labels,thresh=jaccard_thresh)
                if m and ((i,pair[0][0],pair[0][1],pair[1][0],pair[1][1]) not in seen_pred_gold):
                    
                    good_preds.append([i,pair[0][0],pair[0][1]])
                    seen_pred_gold[(i,pair[0][0],pair[0][1],pair[1][0],pair[1][1])]=1
    
    corr_pred = pd.DataFrame(good_preds,columns=["docid","arg0_gold","arg1_gold"])
    corr_pred = corr_pred.drop_duplicates()
    TP = corr_pred.shape[0]
    FP = predrels.shape[0] - TP
    FN = goldrels.shape[0] - TP

    precision = TP/(TP+FP)
    recall = TP/(FN+TP)

    F1 = 2*(precision * recall) / (precision + recall)

    return corr_pred, precision,recall, F1
