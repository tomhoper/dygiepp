"""
Convert coref predictions to `tsv` by:
- Identify an exemplar.
- Writing as .tsv, one line per cluster.
"""

from numpy import argmax


def span_length(span):
    return span.end_doc - span.start_doc + 1


def member_to_text(member):
    # So that we can use "|" as delimiter.
    text = " ".join(member.span.text).replace("|", "/")
    res = f"{text}|{member.span.start_doc}|{member.span.end_doc}"
    return res


def one_doc(doc, f_out):
    clusts = doc.predicted_clusters
    for clust in clusts:
        lengths = [span_length(entry.span) for entry in clust]
        exemplar_ix = argmax(lengths)
        exemplar = clust[exemplar_ix]
        exemplar_text = " ".join(exemplar.span.text)

        fields = [doc.doc_key, str(clust.cluster_id), exemplar_text]
        fields += [member_to_text(member) for member in clust]

        line = "\t".join(fields)
        print(line, file=f_out)


def to_tsv(dataset, fname):
    with open(fname, "w") as f_out:
        for doc in dataset:
            one_doc(doc, f_out)
