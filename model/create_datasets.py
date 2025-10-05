import pandas as pd

from algorithms.sentiment_analysis import get_sentiment
from model.character_aliases import alias_map, double_character_names_map
from read_data import *


def get_unique_characters():
    script = get_script()
    unique_characters = script.get("Character").dropna().unique()
    unique_characters = list(unique_characters)
    for character in unique_characters:
        if len(character.split(" and ")) > 1:
            unique_characters.remove(character)
    unique_characters.remove("Katara and Sokka")
    return unique_characters


def get_all_characters():
    """
    we create a dict of all character names to their official names
    """
    official_character_names = list(get_unique_characters())
    name_map = alias_map.copy()
    for official_character_name in official_character_names:
        name_map[official_character_name] = official_character_name
    return name_map


def __is_character_mentioned_in_a_line(character, line) -> bool:
    """
    matching against character name preceded by a space and followed by either a space or a punctuation mark
    """
    line_lower = line.lower()
    character_lower = character.lower()
    return (f" {character_lower} " in line_lower
            or f" {character_lower}," in line_lower
            or f" {character_lower}." in line_lower
            or f" {character_lower}:" in line_lower
            or f" {character_lower}!" in line_lower)


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
    all_characters = get_all_characters()
    # iterate over all lines in the script
    for index, row in script.iterrows():
        speakers = row["Character"]
        line = row["script"]
        # get the character(s) that is speaking
        if pd.isna(speakers):
            # skipping  line
            continue
        speakers = double_character_names_map[speakers] if speakers in double_character_names_map else [speakers]
        # get the character(s) mentioned in the line
        mention_accounted_for = False
        # todo instead of iterating over each character we could split a line into tokens and do all_characters[token] to see if there's a value. should be faster
        for character_addressed in all_characters.keys():
            if mention_accounted_for:
                # todo not sure if this is right. could there be cases when we want to keep iterating further?
                break
            if __is_character_mentioned_in_a_line(character_addressed, line):
                for speaker in speakers:
                    mentioned = all_characters[character_addressed]
                    record_x_mentions_y = [speaker, mentioned]
                    x_mentions_y.append(record_x_mentions_y)

                    sentiment = get_sentiment(line)
                    record_x_mentions_y_with_sentiment = [speaker, mentioned, sentiment]
                    x_mentions_y_with_sentiment.append(record_x_mentions_y_with_sentiment)
                    mention_accounted_for = True
    x_mentions_y_data_frame = pd.DataFrame(x_mentions_y, columns=["x", "y"])
    x_mentions_y_with_sentiment_data_frame = pd.DataFrame(x_mentions_y_with_sentiment, columns=["x", "y", "sentiment"])
    return x_mentions_y_data_frame, x_mentions_y_with_sentiment_data_frame


def cleanup_edges(data):
    characters = get_characters()
    valid = list(characters.get("name"))
    out = data[data["x"].isin(valid) & data["y"].isin(valid)].reset_index(drop=True)
    return out


def weigh_rows(data):
    weighted = (
        data.value_counts(["x", "y"])
        .rename("weight")
        .reset_index()
    )
    return weighted


def main():
    data = x_speaks_before_y()
    data = cleanup_edges(data)
    weighted = weigh_rows(data)
    weighted.to_csv("./data/x_speaks_to_y.csv", index=False)
    # uncomment this if my code with ./data does not work
    # weighted.to_csv("model/data/x_speaks_to_y.csv", index=False)

    data, data_with_sentiment = x_mentions_y()
    data = cleanup_edges(data)
    data_with_sentiment = cleanup_edges(data_with_sentiment)
    weighted = weigh_rows(data)
    weighted.to_csv("./data/x_mentions_y.csv", index=False)
    data_with_sentiment.to_csv("./data/x_mentions_y_with_sentiment.csv", index=False)

    # uncomment this if my code with ./data does not work
    # weighted.to_csv("model/data/x_mentions_y.csv", index=False)
    # weighted_with_sentiment.to_csv("model/data/x_mentions_y_with_sentiment.csv", index=False)

    return


if __name__ == "__main__":
    main()
