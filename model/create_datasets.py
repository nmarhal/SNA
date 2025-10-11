import pandas as pd
import re
from functools import lru_cache

from algorithms.sentiment_analysis import get_sentiment
from model.character_aliases import alias_map, double_character_names_map
from read_data import *


@lru_cache(maxsize=1024)
def _pattern_for(name: str) -> re.Pattern:
    parts = re.split(r'\s+', name.strip())
    # If you want to allow punctuation between words, use r'\W+' instead of r'\s+'
    pat = r'(?<!\w)' + r'\s+'.join(map(re.escape, parts)) + r'(?!\w)'
    return re.compile(pat, re.IGNORECASE)

def has_name(line: str, character_name: str) -> bool:
    return bool(_pattern_for(character_name).search(line))

def x_speaks_before_y():
    """
    Simple connection where a character x spoke their line before character y
    Gives a rough "x speaks to y" relationship network, but will have false edges
    """
    script = get_script()
    previous_character = None
    x_speaks_to_y = []  # we will add edges to this list
    for index, row in script.iterrows():
        character = row["Character"]
        if previous_character is None:  # there is no x, go to next line
            if pd.isna(character):
                previous_character = None
            else:
                previous_character = character
            continue
        if pd.isna(character):  # there is no y, go to next line
            previous_character = None
            continue
        # Sometimes there are characters in the script called "Sokka and Katara" in this case we awant to
        # split these names and add an edge for "Sokka" and an edge for "Katara"
        x = double_character_names_map[character] if character in double_character_names_map else [character]
        y = double_character_names_map[previous_character] if previous_character in double_character_names_map else [
            previous_character]
        for i in x:
            for j in y:
                i = i.lower()
                j = j.lower()
                x_speaks_to_y.append([i, j])
        # We set our current character as previous character for the next loop
        previous_character = character
    return pd.DataFrame(x_speaks_to_y, columns=["x", "y"])


def x_mentions_y():
    """
    x mentions y in a line, uses the official character names as well as as many aliases as I could find specified
    in the alias map
    """
    x_mentions_y = []
    x_mentions_y_with_sentiment = []
    # we load the script
    script = get_script()
    # we create a dict of all character names to their official names
    official_character_names = get_characters()["name"]
    name_map = alias_map.copy()
    for official_character_name in official_character_names:
        official_character_name = official_character_name.lower()
        name_map[official_character_name] = official_character_name
    name_list = sorted(list(name_map.keys()))
    for i in range(len(name_list)):
        name_list[i] = name_list[i].lower()
    name_set = sorted(set(name_list))
    # iterate over all lines in the script
    for index, row in script.iterrows():
        speakers = row["Character"]
        full_line = row["script"]
        line = re.sub(r"\[.*?\]", "", full_line)
        # get the character(s) that is speaking
        if pd.isna(speakers):
            # skipping  line
            continue
        speakers = double_character_names_map[speakers] if speakers in double_character_names_map else [speakers]
        # get the character(s) mentioned in the line
        for character_addressed in name_set:
            character_addressed = character_addressed.lower()
            if has_name(line=line, character_name=character_addressed):
                for speaker in speakers:
                    speaker = speaker.lower()
                    character_addressed = name_map[character_addressed].lower()
                    sentiment = get_sentiment(line)
                    record_x_mentions_y_with_sentiment = [speaker, character_addressed, sentiment]
                    x_mentions_y_with_sentiment.append(record_x_mentions_y_with_sentiment)
                    x_mentions_y.append([speaker, character_addressed])
    x_mentions_y_data_frame = pd.DataFrame(x_mentions_y, columns=["x", "y"])
    x_mentions_y_with_sentiment_data_frame = pd.DataFrame(x_mentions_y_with_sentiment, columns=["x", "y", "sentiment"])
    return x_mentions_y_data_frame, x_mentions_y_with_sentiment_data_frame

def cleanup_edges(data):
    characters = get_characters()
    valid = list(characters.get("name"))
    valid = [x.lower() for x in valid]
    out = data[data["x"].isin(valid) & data["y"].isin(valid)].reset_index(drop=True)
    return out


def weigh_rows(data):
    weighted = (
        data.value_counts(["x", "y"])
        .rename("weight")
        .reset_index()
    )
    return weighted

def lower_dataset(data):
    data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    return data

def main():
    data = x_speaks_before_y()
    data = cleanup_edges(data)
    weighted = weigh_rows(data)
    # weighted.to_csv("./data/x_speaks_to_y.csv", index=False)
    # uncomment this if my code with ./data does not work
    weighted.to_csv("model/data/x_speaks_to_y.csv", index=False)

    data, data_with_sentiment = x_mentions_y()
    data = cleanup_edges(data)
    data_with_sentiment = cleanup_edges(data_with_sentiment)
    weighted = weigh_rows(data)
    # weighted.to_csv("./data/x_mentions_y.csv", index=False)
    # data_with_sentiment.to_csv("./data/x_mentions_y_with_sentiment.csv", index=False)
    # uncomment this if my code with ./data does not work
    weighted.to_csv("model/data/x_mentions_y.csv", index=False)
    data_with_sentiment.to_csv("model/data/x_mentions_y_with_sentiment.csv", index=False)

    return


if __name__ == "__main__":
    main()
