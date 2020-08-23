import utils as ut
import argparse


if __name__ == "__main__":
  parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

  parser.add_argument('--data_tsv_paht',
                      type=str,
                      default="corrections/tsvs/corrections_tom.tsv",
                      help='annotator name, comma seperated',
                      required=False)
  args = parser.parse_args()

  data_list = []
  input_file = open(args.data_tsv_paht)
  for line in input_file:
      line_parts = line[:-1].split("\t")
      if line_parts[5] == "accept":
          data_list.append(line_parts[0:4])
  ut.length_distributions(data_list)
