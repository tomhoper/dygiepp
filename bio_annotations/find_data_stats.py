import utils as ut
import argparse

def find_partitions_abstract_rel_count(data_list, data_tsv_paht):
    print("data set stats is for " + data_tsv_paht)
    print("number of relations is " + str(len(data_list)))
    partition_count = []
    abstract_count = []
    for data in data_list:
      if data[0] not in abstract_count:
        abstract_count.append(data[0])
      if (data[0], data[1]) not in partition_count:
        partition_count.append((data[0], data[1]))
    print("number of partitions is " + str(len(partition_count)))
    print("number of abstracts is " + str(len(abstract_count)))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

  parser.add_argument('--data_tsv_paht',
                      type=str,
                      default="validations/madeline_final.tsv",
                      required=False)
  args = parser.parse_args()

  data_list = []
  input_file = open(args.data_tsv_paht)
  for line in input_file:
      line_parts = line[:-1].split("\t")
      if line_parts[5] == "accept":
          data_list.append(line_parts[0:4])

  # find_partitions_abstract_rel_count(data_list, args.data_tsv_paht)

  # ut.length_distributions(data_list)
  ut.find_stats_span_distance(data_list)
