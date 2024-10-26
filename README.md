# AudioSet Dataset Downloader

Toolkit for downloading the audio files from the [AudioSet](https://research.google.com/audioset/) dataset.

## AudioSet Overview

AudioSet consists of an expanding ontology of 632 audio event classes and a collection of 2,084,320 human-labeled 10-second sound clips drawn from YouTube videos. The ontology is specified as a hierarchical graph of event categories, covering a wide range of human and animal sounds, musical instruments and genres, and common everyday environmental sounds.

## Setup

First of all you need to download the dependecies to use the code. You can do that running the following code:

```	
pip install -r requirements.txt
```	

It's recommended to use virtualenv or conda virtual environment before installing the dependencies.

## How to Use

To run the code is very straight forward, you just need to do:

```python3 
python3 main.py
```

There is some optinal parameters you can use as you need:
- `-labels_file` or `--labels_file`: The main csv ('class_labels_indices.csv') path. If none, the file will be downloaded and saved in the folder root path. Default: None.
- `-fs` or `--fs`: The frame sample (or sample rate) in Hz (8000 or 16000) which you want to save the videos. Default: 16000.
- `-o` or `--o`: The output path where you want to save the downloaded videos. If none, will be created a folder named "dataset" on the folder root path. Default: None.
- `-multiprocessing` or `--multiprocessing`: Use it if you want to use multiprocessing to speed up the process.
- `-overwrite` or `--overwrite`: Use it if you want to overwrite the files that have already beed downloaded.
- `-c` or `--c`: The class(es) you want to download. You can pass just one class or more. See the examples section below to see how to use. Default: all classes will be downloaded.
- `-max_files` or `--max_files`: The maximum files for each class that you want to download. Default: None, all files will be downloaded.
- `-dataset` or `--dataset`: Which dataset you want to use ('eval', 'balanced-train', 'unbalanced-train').

## Examples

Download the videos from a specific classes:

```python3 
python3 main.py --c bell
```

or

```python3 
python3 main.py --c bell alarm explosion
```

Download the videos from a specific dataset:

```python3 
python3 main.py --dataset balanced-train
```

Using multiprocessing to speed up the process:

```python3 
python3 main.py --multiprocessing
```

Overwritting existing files that already have been downloaded:

```python3 
python3 main.py --overwrite
```

Passing the label_csf folder

```python3 
python3 main.py --labels_file {FOLDER_ROOT_PATH}
```

Download a max amount of videos from each specific classes:

```python3 
python3 main.py --c bell explosion --max_files 10
```

Using everything together:

```python3 
python3 main.py --c bell explosion --fs 8000 --max_files 100 --multiprocessing --overwrite
```

In this case I want to download 100 videos from the "bell" and "explosion" classes, resample than to have a frame sample of 8000 Hz, use multiprocessing to speed up the process and overwrite all the files (if any files have already been downloaded).

## Project's Structure
```
audioset-downloader
├── src
|   └── core.py
├── __init__.py
├── LICENCE
├── main.py
├── setup.py
├── requirements.txt
└── README.md
```

## Author
- [Rafael Greca](https://github.com/rafaelgreca)