import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_script():
    data = pd.read_csv(os.path.join(DATA_DIR, "ATLA-episodes-scripts.csv"))
    return data

def get_x_mentions_y():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_mentions_y.csv"))
    return data

def get_data_frames_from_directory(dir_name: str):
    books_dir = os.path.join(DATA_DIR, dir_name)
    book_files = [file for file in os.listdir(books_dir) if file.endswith(".csv")]
    data_frames = []
    for file in book_files:
        data_frame = pd.read_csv(os.path.join(DATA_DIR, file))
        data_frames.append(data_frame)
    return data_frames

def get_x_mentions_y_per_book() -> list[pd.DataFrame]:
    return get_data_frames_from_directory("books")

def get_x_mentions_y_per_episode() -> list[pd.DataFrame]:
    return get_data_frames_from_directory("episodes")

def get_x_speaks_to_y():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_speaks_to_y.csv"))
    return data

def get_characters():
    data = pd.read_csv(os.path.join(DATA_DIR, "characters.csv"))
    return data

def get_x_speaks_to_y_sentiment():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_mentions_y_with_sentiment_and_line.csv"))
    return data