import json
import itertools
import copy


def load_jsonl(fname):
    return [json.loads(x) for x in open(fname)]


def save_jsonl(xs, fname):
    with open(fname, "w") as f:
        for x in xs:
            print(json.dumps(x), file=f)


def overlaps(clust1, clust2):
    # If they share a span exactly, they overlap.
    for span1, span2 in itertools.product(clust1, clust2):
        if span1 == span2:
            return True

    # Otherwise, return they don't.
    return False


def is_contained_in(contained, container):
    "Return True if the smaller one is contained in the bigger one."
    return ((contained[0] >= container[0]) and
            (contained[1] <= container[1]) and
            (contained != container))


def merge(clust1, clust2):
    members = sorted(set(clust1 + clust2))

    deduped_members = set()
    for member in members:
        append = True
        for container in members:
            # If this span is contained in another span, skip it.
            is_contained = is_contained_in(member, container)
            append = append and not is_contained
            # If we've already got this span, skip it.
        if append:
            deduped_members.add(member)

    merged = tuple(sorted(deduped_members))
    return merged


def merge_doc(doc1, doc2):
    # Convert to tuples.
    all_clusters_list = doc1["predicted_clusters"] + doc2["predicted_clusters"]
    all_clusters = []
    for clust in all_clusters_list:
        to_append = tuple([tuple(x) for x in clust])
        all_clusters.append(to_append)

    merged = []
    unmerged = copy.deepcopy(all_clusters)

    to_merge = copy.deepcopy(all_clusters)

    while to_merge:
        clust = to_merge.pop(0)

        # Find a candidate to merge.
        found_one = False
        for candidate in unmerged + merged:
            if candidate == clust:
                continue
            if overlaps(clust, candidate):
                found_one = True
                break

        # If we found one, create a new cluster.
        if found_one:
            new_cluster = merge(clust, candidate)

            # Remove the old cluster and candidate.
            for container in merged, unmerged:
                for contained in clust, candidate:
                    if contained in container:
                        container.remove(contained)

            # Add the new cluster to the list of merged clusters, and to the stack.
            merged.append(new_cluster)
            to_merge.append(new_cluster)

    # Convert to list and return.
    merged_list = []
    for entry in merged:
        to_append = [list(x) for x in entry]
        merged_list.append(to_append)

    doc_res = copy.deepcopy(doc1)
    doc_res["predicted_clusters"] = merged_list

    return doc_res


####################


dataset_scierc = load_jsonl("results/predictions/scierc.jsonl")
dataset_both = load_jsonl("results/predictions/genia-scierc.jsonl")

dataset_merged = []
for doc_scierc, doc_both in zip(dataset_scierc, dataset_both):
    doc_merged = merge_doc(doc_scierc, doc_both)
    dataset_merged.append(doc_merged)


save_jsonl(dataset_merged, "results/predictions/merged.jsonl")
