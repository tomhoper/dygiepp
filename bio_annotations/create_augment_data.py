# This script fills in the black with coref and transivity the new dataset containing the relations will be then written to the root directory

import argparse
import utils as ut
import dataset_creator as dc


def find_transivity_relations(golddf):
    rels = golddf[["id","arg0","arg1","rel", "text"]]#.drop_duplicates()
    rels = rels.drop_duplicates(subset =["id","arg0","arg1","text"]).set_index("id")
    new_added = True
    seen_new = []
    while new_added:
        new_list = [x for x in rels.iterrows()]
        new_added = False
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
                  if "text" in rels.columns:
                    new_data['text']: [row1[1]['text']]
                  
                  seen_new.append((row1[1]['arg0'], row2[1]['arg1']))
                  df = pd.DataFrame(new_data).set_index("id",inplace=False)
                  rels = rels.append(df)
                  new_added = True

    return rels

def write_augmented_tsv(args):
    

    new_rels = find_transivity_relations(golddf)





if __name__ == '__main__':

    parser = argparse.ArgumentParser()  # pylint: disable=invalid-name

    parser.add_argument('--root',
                        type=Path,
                        help='./',
                        required=True)
    parser.add_argument('--mech_effect_mode',
                        action='store_true')

    parser.add_argument('--current_gold',
                      type=str,
                      default="2222",
                      help='The path to the current tsv file containing the annotations',
                      required=False)


    args = parser.parse_args()

    #step0 read the data
    if args.mech_effect_mode == True:
        new_gold_path = pathlib.Path(args.root) / 'gold_augment' /  'mech_effect' / 'gold_par.tsv'

    if args.mech_effect_mode == False:
        new_gold_path = pathlib.Path(args.root) / 'gold_augment' /  'mech' / 'gold_par.tsv'


    GOLD_PATH = pathlib.Path(gold_path)

    golddf = pd.read_csv(GOLD_PATH, sep="\t",header=None, names=["id","text","arg0","arg1","rel","y"])
    golddf = golddf[golddf["y"]=="accept"]

    #step 1: get transivity of the relations 





