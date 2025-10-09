import pandas as pd

# the code was breaking for me when using model/data ... bc the read_data file is in the model dir
# if it doesn't work for you guys just comment out my lines and uncomment the old ones
def get_script():
    # data = pd.read_csv("./data/ATLA-episodes-scripts.csv")
    data = pd.read_csv("model/data/ATLA-episodes-scripts.csv")
    return data

def get_x_mentions_y():
    data = pd.read_csv("model/data/x_mentions_y.csv")
    #data = pd.read_csv("./data/x_mentions_y.csv")
    return data

def get_x_speaks_to_y():
    data = pd.read_csv("model/data/x_speaks_to_y.csv")
    # data = pd.read_csv("./data/x_speaks_to_y.csv")
    return data

def get_characters():
    data = pd.read_csv("model/data/characters.csv")
    # data = pd.read_csv("./data/characters.csv")
    return data

def get_accepted_character_names():
    data = pd.read_csv("model/data/characters.csv")
    return list(data["name"])

if __name__ == "__main__":
    get_script()