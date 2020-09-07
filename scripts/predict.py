# Predict, then uncollate



if __name__ == '__main__':
    parser.add_argument('--root',
                        type=Path,
                        help='/data/aida/covid_aaai/',
                        required=False)
    parser = argparse.ArgumentParser() 

    parser.add_argument('--test_data',
                        action='store_true')
    
    parser.add_argument('--test_index',
                        type=int,
                        default=0)

    args = parser.parse_args()

     # test_dir = pathlib.Path(args.root) / 'UnifiedData' / args.test_path_combo / 'mapped' / 'mech_effect' 
    serial_dir = pathlib.Path(args.root) / 'experiments' / "events" / 'mapped' / 'mech_effect'
    if args.test_data:
      collated_pred_dir = pathlib.Path(args.root) / 'predictions' / "events" / 'mapped_collated' / 'mech_effect'
      pred_dir = pathlib.Path(args.root) / 'predictions' / "events" / 'mapped' / 'mech_effect'
    else:
      collated_pred_dir = pathlib.Path(args.root) / 'predictions_dev' / "events" / 'mapped_collated' / 'mech_effect'
      pred_dir = pathlib.Path(args.root) / 'predictions_dev' / "events" / 'mapped' / 'mech_effect'
    
    test_dir = "/home/aida/covid_clean/dygiepp/data/processed/collated/"
    if args.test_data:
      test_dir = pathlib.Path(test_dir) /'test.json'
    else:
      test_dir = pathlib.Path(test_dir) /'dev.json'
   

    for file in os.listdir(str(serial_dir)):
    trail_strat_str = "run_"
    if args.test_data:
      trail_strat_str = trail_strat_str + str(args.test_index)

    if file.startswith(trail_strat_str):
        run_serial_dir = serial_dir / file / "trial"
        run_pred_dir = collated_pred_dir / file 
        uncollate_pred_dir = pred_dir / file
        run_pred_dir.mkdir(parents=True, exist_ok=True)
        uncollate_pred_dir.mkdir(parents=True, exist_ok=True)
        
        
        pred_path = pathlib.Path(run_pred_dir) / "pred.json"
        uncollated_pred_path = uncollate_pred_dir.Path(run_pred_dir) / "pred.json"


        allennlp_command = [
                  "allennlp",
                  "predict",
                  str(run_serial_dir),
                  str(test_dir),
                  "--predictor dygie",
                  "--include-package dygie",
                  "--use-dataset-reader",
                  "--output-file",
                  str(pred_path),
                  "--cuda-device",
                  "0"
          ]
        print(" ".join(allennlp_command))
        try:
          subprocess.run(" ".join(allennlp_command), shell=True, check=True)
          ds = Dataset(pred_path)

          in_dir = f"results/predictions/collated/{model}"
          out_dir = f"results/predictions/final/{model}"
          os.makedirs(out_dir, exist_ok=True)
          cmd = ["python", "scripts/data/shared/uncollate.py",
                 str(run_pred_dir),
                 str(uncollate_pred_dir),
                 "--order_like=data/cleanup/covid",
                 "--file_extension=json",
                 "--train_name=skip"]
          subprocess.run(cmd)
          prediction_to_tsv(ds, pathlib.Path(uncollate_pred_dir) / "pred.tsv")
        except:
          pass





# uncollate=scripts/data/shared/uncollate.py

# # Only do pubmebert, since it gets slightly better results.
# config_name="covid-event-pubmedbert"

# pred_dir=results/predictions/$config_name
# collated_dir=$pred_dir/collated
# uncollated_dir=$pred_dir/uncollated


# mkdir -p $collated_dir
# mkdir -p $uncollated_dir


    
