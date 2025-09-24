import pandas as pd

def get_script():
    data = pd.read_csv("model/data/ATLA-episodes-scripts.csv")
    return data

def get_x_mentions_y():
    data = pd.read_csv("model/data/x_mentions_y.csv")
    return data

def get_x_speaks_to_y():
    data = pd.read_csv("model/data/x_speaks_to_y.csv")
    return data

def get_characters():
    data = pd.read_csv("model/data/characters.csv")
    return data