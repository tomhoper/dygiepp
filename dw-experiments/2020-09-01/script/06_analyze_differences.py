"""
Analyze differences in the predictions made by the different models.
"""

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from numpy import random as npr

from dygie.data.dataset_readers import document

from report import Report

dataset_scierc = document.Dataset.from_jsonl("results/predictions/scierc.jsonl")
dataset_both = document.Dataset.from_jsonl("results/predictions/genia-scierc.jsonl")

n_clusters = []
n_clusters = {"scierc": [], "scierc_genia": []}
n_cluster_members = []

n_clusters = {
    "scierc": [len(entry.predicted_clusters) for entry in dataset_scierc],
    "both": [len(entry.predicted_clusters) for entry in dataset_both],
    }

n_cluster_members = {"scierc": [], "both": []}

for entry in dataset_scierc:
    n_clust = [len(x.members) for x in entry.predicted_clusters]
    n_cluster_members["scierc"].extend(n_clust)

for entry in dataset_both:
    n_clust = [len(x.members) for x in entry.predicted_clusters]
    n_cluster_members["both"].extend(n_clust)


report = Report(report_name="results/prediction-differences")
msg = ("The 'scierc' model is trained on scierc only; the 'both' model"
       "is trained on GENIA + SciERC")
report.write(msg)

# Scatter the number of coref clusters.
n_clusters = pd.DataFrame(n_clusters)
npr.seed(76)
jitter = npr.uniform(-0.1, 0.1, size=n_clusters.values.shape)
jittered = n_clusters + jitter

n_cluster_members = {k: pd.Series(v) for k, v in n_cluster_members.items()}

sns.jointplot(x="scierc", y="both", data=jittered, alpha=0.4)
fig = plt.gcf()
fig_file = "fig/n-clusters-scatter.png"
fig.savefig(fig_file)
desc = ("Each point is a document. The x and y-coordinates shown the number of"
        " predicted clusters for that document, for the model trained on SciERC"
        " and on both")
report.add_fig(fig_file, description=desc)

# Histogram of clusters per doc.
msg = """The SciERC model tends to predict a small number of large clusters,
while the GENIA + SciERC model tends to predict a large number of small clusters.
"""
report.write(msg)
fig, ax = plt.subplots(1, figsize=[8, 4])
ix = [x for x in range(11)]
colors = plt.cm.tab10.colors

for color, k in zip(colors[:2], n_clusters.columns):
    col = n_clusters[k]
    counts = col.value_counts().sort_index().reindex(ix).fillna(0)
    counts.plot.bar(ax=ax, label=k, alpha=0.4, color=color)

ax.set_xlabel("# clusters per doc")
ax.set_ylabel("Count")
ax.legend()
ax.set_title("Number of coref clusters per doc")
fig.tight_layout()
fig_file = "fig/n-clusters-hist.png"
fig.savefig(fig_file)
report.add_fig(fig_file)


# Count the number of members per cluster.
max_counts = 0
for k, v in n_cluster_members.items():
    max_counts = max(max_counts, v.value_counts().max())

ix = [x for x in range(21)]


fig, ax = plt.subplots(1, figsize=[8, 4])
for color, (k, v) in zip(colors[:2], n_cluster_members.items()):
    counts = v.value_counts().sort_index().reindex(ix).fillna(0)
    counts.plot.bar(ax=ax, label=k, alpha=0.4, color=color)

ax.set_xlabel("# cluster members")
ax.set_ylabel("Count")
ax.legend()

ax.set_title("Coreference cluster sizes")
fig.tight_layout()

fig_file = "fig/n-cluster-members.png"
fig.savefig(fig_file)
report.add_fig(fig_file)

report.render_pdf()
