from typing import List, Union

import csv
import os
import pandas as pd
import multiprocessing
import logging

## create the log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("./logging.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def create_csv(labels_files_dir: str) -> pd.DataFrame:
    """
    Transforms the original csv to a new formated csv.

    Param:
        :labels_files_dir: The dataset path location.
    Return:
        The new formated csv cointaining all the videos from all the classes.
    """
    new_df = pd.DataFrame()

    with open(labels_files_dir, "r") as df:
        rows = csv.reader(df, delimiter=",")
        line_count = 0
        
        for row in rows:
            if line_count == 0 or line_count == 1 or line_count == 2:
                line_count += 1
                continue
            else:
                youtube_id, start_timestamp, end_timestamp, labels = row[0], row[1], row[2], row[3:]
                
                for i, label in enumerate(labels):
                    labels[i] = str(label.replace("\"", "").replace("'", "").strip())
                
                total_labels = len(labels)
                row = pd.DataFrame({"youtube_id": [youtube_id.strip()] * total_labels,
                                    "start_timestamp": [start_timestamp.strip()] * total_labels,
                                    "end_timestamp": [end_timestamp.strip()] * total_labels,
                                    "mid": labels})
                new_df = pd.concat([new_df, row], axis=0)
                del row

    return new_df

def download_dataset_files(dataset: str) -> None:
    """
    If the main csv file isn't in the root path, then download it.

    Param:
        :dataset: The dataset name that will be used to download the videos.
    Return:
        None
    """
    os.system(f"wget -c storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/{dataset} -q")
    os.system("wget -c storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv -q")

def _aux_download_file(video_id: str,
                       start_timestamp: float,
                       end_timestamp: float,
                       label: str) -> None:
    """
    Auxiliar function to download the videos.

    Param:
        :video_id: The YouTube's video id.
        :start_timestamp: The beggining of the video segment.
        :end_timestamp: The end of the video segment.
        :label: The corresponding label to that video segment.
    Return:
        None
    """
    try:
        label = label.split(",")[0].replace(" ", "_")
        os.makedirs(f"{PATH_OUTPUT}/{label}", exist_ok=True)
        youtube_dl_command = f"youtube-dl -f bestaudio -g https://www.youtube.com/watch?v={video_id} -i"
        ffmpeg_command = f"ffmpeg -{OVERWRITE_FILE} -ss {start_timestamp} -to {end_timestamp} -i $({youtube_dl_command}) " + \
                        f"-ar {FRAME_SAMPLE} -hide_banner -v quiet {PATH_OUTPUT}/{label}/{video_id}-{start_timestamp}-{end_timestamp}.wav"
        
        if os.system(ffmpeg_command) != 0:
            raise Exception(f"Could not download video {video_id}")
    except:
        logger.error(f"Could not download video {video_id}")

def download_files(df: pd.DataFrame,
                   use_multiprocessing: bool,
                   output_path: str,
                   fs: int,
                   max_files: Union[None, int],
                   classes: List,
                   overwrite: bool) -> None:
    """
    Main function responsible to download the videos.

    Param:
        :df: The csv containing 
        :use_multiprocessing: Use multiprocessing or not.
        :output_path: Path where the downloaded videos will be saved.
        :fs: Frame sample of the video.
        :max_files: Max files to be downloaded for each class.
        :classes: Class(es) that will be downloaded.
        :overwrite: Overwrite or not the files (if already exists).
    Return:
        None
    """
    global OVERWRITE_FILE
    global FRAME_SAMPLE
    global PATH_OUTPUT

    if overwrite:
        OVERWRITE_FILE = 'y'
    else:
        OVERWRITE_FILE = 'n'
    
    FRAME_SAMPLE = fs
    PATH_OUTPUT = output_path

    ## if max_files param isn't none, create a dictionary
    ## to keep track how many files have already been downloaded
    ## from each class
    if max_files != None:
        count_classes = {c:0 for c in classes}

    if use_multiprocessing:
        num_workers = multiprocessing.cpu_count() - 1
        pool = multiprocessing.Pool(num_workers)

        for i, infos in enumerate(zip(df["youtube_id"],
                                      df["start_timestamp"],
                                      df["end_timestamp"],
                                      df["display_name"])):

            if max_files != None:
                ## check if we have passed the max files amount for that class
                if count_classes[df.iloc[i, 4]] < max_files:                
                    pool.starmap_async(_aux_download_file, [infos])
                    count_classes[df.iloc[i, 4]] += 1
                else:
                    ## check if we have passed the max files amount for all the classes
                    is_over = all([count_classes[c] > max_files for c in count_classes.keys()])
                    if is_over: break;
            else:
                pool.starmap_async(_aux_download_file, [infos])

        pool.close()
        pool.join()

    else:
        for i, (video_id, start_timestamp, end_timestamp, label) in enumerate(zip(df["youtube_id"],
                                                                                  df["start_timestamp"],
                                                                                  df["end_timestamp"],
                                                                                  df["display_name"])):
            
            if max_files != None:
                ## check if we have passed the max files amount for that class
                if count_classes[df.iloc[i, 4]] < max_files:           
                    _aux_download_file(video_id, start_timestamp, end_timestamp, label)
                    count_classes[df.iloc[i, 4]] += 1
                else:
                    ## check if we have passed the max files amount for all the classes
                    is_over = all([count_classes[c] >= max_files for c in count_classes.keys()])
                    if is_over: break
            else:
                _aux_download_file(video_id, start_timestamp, end_timestamp, label)