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

def get_data_frames_from_directory(dir_name: str, file_number: int = None):
    sections_dir = os.path.join(DATA_DIR, dir_name)
    section_files = sorted([file for file in os.listdir(sections_dir) if file.endswith(".csv")])
    if file_number is not None:
        section_files = [section_files[file_number - 1]]
    data_frames = []
    for file in section_files:
        data_frame = pd.read_csv(os.path.join(sections_dir, file))
        data_frames.append(data_frame)
    return data_frames

def get_x_mentions_y_per_book() -> list[pd.DataFrame]:
    return get_data_frames_from_directory("books")

def get_x_mentions_y_for_book_number(book_number: int):
    return get_data_frames_from_directory("books", file_number=book_number)[0]

def get_x_mentions_y_per_episode() -> list[pd.DataFrame]:
    return get_data_frames_from_directory("episodes")

def get_x_mentions_y_for_episode_number(episode_number: int):
    return get_data_frames_from_directory("episodes", file_number=episode_number)[0]

def get_x_speaks_to_y():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_speaks_to_y.csv"))
    return data

def get_characters():
    data = pd.read_csv(os.path.join(DATA_DIR, "characters.csv"))
    return data

def get_x_speaks_to_y_sentiment():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_mentions_y_with_sentiment_and_line.csv"))
    return data