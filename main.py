from src.core import download_files, download_dataset_files, create_csv

import argparse
import os
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audioset dataset downloader")
    parser.add_argument("-dataset", "--dataset", type=str, help="The dataset you want to use (str)")
    parser.add_argument("-labels_file", "--labels_file", type=str, help="Labels file directory (str)")
    parser.add_argument("-fs", "--fs", type=int, help="Sample rate in Hz (int). Default: 16000")
    parser.add_argument("-o", "--o", type=str, help="Output directory (str). Default: root_directory_folder/dataset")
    parser.add_argument("-multiprocessing", "--multiprocessing", action="store_true", dest="multiprocessing", help="Use multiprocessing (bool). Default: False")
    parser.add_argument("-overwrite", "--overwrite", action="store_true", dest="overwrite", help="Overwrite existing files (bool). Default: False")
    parser.add_argument("-c", "--c", nargs="+", type=str.lower, help="Specify the classes you want to download (str). Default: all")    
    parser.add_argument("-max_files", "--max_files", type=int, help="Max files to download from each class (int). Default: None (all of them)")
    parser.set_defaults(
        fs=16000,
        multiprocessing=False,
        overwrite=False,
        o=os.path.join(os.getcwd(), "dataset"),
        labels_file=None,
        c="all",
        max_files=None,
        dataset="balanced-train"
    )
    args = parser.parse_args()

    all_datasets = ["eval", "balanced-train", "unbalanced-train"]
    available_fs = [8000, 16000]

    assert args.fs in available_fs, f"The fs must be {available_fs}"
    assert args.dataset in all_datasets, f"The dataset must be one of {all_datasets}"
    assert ((args.max_files == None) or ((type(args.max_files) == int) and (args.max_files > 0))), f"You must provide a valid value for max_files or let it empty to download everything"

    if args.dataset == "eval":
        dataset = "eval_segments.csv"
    elif args.dataset == "balanced-train":
        dataset = "unbalanced_train_segments.csv"
    elif args.dataset == "unbalanced-train":
        dataset = "balanced_train_segments.csv"

    ## creating the output path folder if doesn't exists already
    os.makedirs(args.o, exist_ok=True)

    ## if the labels_file path is None, then download the main csv file
    if args.labels_file == None:
        download_dataset_files(dataset=dataset)
        labels_files_dir = os.path.join(os.getcwd(), dataset)
        classes_files_dir = os.path.join(os.getcwd(), "class_labels_indices.csv")
    else:
        ## check if the labels_file path exists
        assert os.path.exists(args.labels_file)

        ## check if the main csv is in the labels_file path
        assert os.path.exists(os.path.join(args.labels_file, dataset)), f"You need to download the {dataset.replace('.csv', '')} csv file or keep the labels_file param None"

        ## check if the classes csv is in the labels_file path
        assert os.path.exists(os.path.join(args.labels_file, "class_labels_indices.csv")), f"You need to download the class_labels_indices csv file or keep the labels_file param None"
    
        labels_files_dir = os.path.join(args.labels_file, dataset)
        classes_files_dir = os.path.join(args.labels_file, "class_labels_indices.csv")    

    
    df = create_csv(labels_files_dir=labels_files_dir) 
    all_classes = pd.read_csv(classes_files_dir, sep=",")
    all_classes["display_name"] = all_classes["display_name"].apply(lambda x: x.lower())
    df = pd.merge(df, all_classes, on="mid")
    df = df[["youtube_id", "start_timestamp", "end_timestamp", "mid", "display_name"]].reset_index(drop=True)
    
    ## some classes has two names, like: "domestic animals, pets"
    ## so we will split them and duplicate the row
    df["display_name"] = df["display_name"].replace(r"\(.+\)", "", regex=True)
    df["display_name"] = df["display_name"].str.split(",")
    df = df.explode("display_name").reset_index(drop=True)
    df["display_name"] = df["display_name"].apply(lambda x: x.strip())
    classes_availables = df["display_name"].unique().tolist()
    
    ## filter the classes to keep only what we want to download
    ## mapping the chosen classes
    if args.c != "all":
        assert all([c.lower() in classes_availables for c in args.c]), f"The class(es) must be {classes_availables}"
        df = pd.concat([df[df["display_name"] == c] for c in args.c], axis=0)
        classes = df["display_name"].unique().tolist()
    else:
        classes = df["display_name"].unique().tolist()
    
    ## download the files
    download_files(df=df,
                   use_multiprocessing=args.multiprocessing,
                   output_path=args.o,
                   fs=args.fs,
                   max_files=args.max_files,
                   classes=classes,
                   overwrite=args.overwrite)