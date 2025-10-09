import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_script():
    data = pd.read_csv(os.path.join(DATA_DIR, "ATLA-episodes-scripts.csv"))
    return data

def get_x_mentions_y():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_mentions_y.csv"))
    return data

def get_x_speaks_to_y():
    data = pd.read_csv(os.path.join(DATA_DIR, "x_speaks_to_y.csv"))
    return data

def get_characters():
    data = pd.read_csv(os.path.join(DATA_DIR, "characters.csv"))
    return data