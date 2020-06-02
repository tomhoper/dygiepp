import allennlp_models.syntax.srl
from allennlp.predictors.predictor import Predictor
import pandas as pd
import re
import itertools
import scispacy
import spacy
import numpy as np
from collections import defaultdict


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

def relation_matching(pair,metric,thresh=0.5):
      match = False
      p1 = pair[0]
      p2 = pair[1]
      if metric =="substring":
        if p1[0] in p2[0] or p2[0] in p1[0]:
            if p1[1] in p2[1] or p2[1] in p1[1]:
                match=True
      elif metric =="jaccard":
        j0 = jaccard_similarity(p1[0].split(),p2[0].split())
        j1 = jaccard_similarity(p1[1].split(),p2[1].split())
        if j0>=thresh and j1>=thresh :
            match=True

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

    nlp = spacy.load("en_core_sci_sm")

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

def ie_eval(relations,golddf,match_metric="substring",jaccard_thresh=0.5):
    goldrels = golddf[["id","arg0","arg1"]]#.drop_duplicates()
    goldrels = goldrels.drop_duplicates().set_index("id")
    predrels = relations.set_index("id",inplace=False)

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
                m = relation_matching(pair,metric=match_metric,thresh=jaccard_thresh)
                if m and ((i,pair[0][0],pair[0][1],pair[1][0],pair[1][1]) not in seen_pred_gold):
                    good_preds.append([i,pair[0][0],pair[0][1],pair[1][0],pair[1][1]])
                    seen_pred_gold[(i,pair[0][0],pair[0][1],pair[1][0],pair[1][1])]=1
    
    corr_pred = pd.DataFrame(good_preds,columns=["docid","arg0_gold","arg1_gold","arg0_pred","arg1_pred"])
    TP = corr_pred.shape[0]
    FP = predrels.shape[0] - TP

    FN = goldrels.shape[0] - TP

    precision = TP/(TP+FP)
    recall = TP/FN

    F1 = 2*(precision * recall) / (precision + recall)

    return corr_pred, precision,recall, F1
