import pandas as pd

from algorithms.sentiment_analysis import get_sentiment
from read_data import *

alias_map = {
    # --- Team Avatar core ---
    "aang": "Aang",
    "avatar": "Aang",
    "the avatar": "Aang",
    "avatar aang": "Aang",
    "sifu hotman": "Aang",
    "hotman": "Aang",
    "twinkletoes": "Aang",
    "twinkle toes": "Aang",
    "little monk": "Aang",
    "the boy in the iceberg": "Aang",

    "katara": "Katara",
    "master katara": "Katara",
    "sifu katara": "Katara",
    "the painted lady": "Katara",
    "painted lady": "Katara",
    "sugar queen": "Katara",
    "healer": "Katara",
    "waterbender girl": "Katara",
    "water tribe girl": "Katara",

    "sokka": "Sokka",
    "captain sokka": "Sokka",
    "boomerang guy": "Sokka",
    "meat and sarcasm guy": "Sokka",
    "idea guy": "Sokka",
    "plan guy": "Sokka",
    "snoozles": "Sokka",
    "water tribe boy": "Sokka",

    "toph": "Toph",
    "toph beifong": "Toph",
    "beifong": "Toph",
    "the blind bandit": "Toph",
    "blind bandit": "Toph",
    "melon lord": "Toph",
    "the melon lord": "Toph",

    "suki": "Suki",
    "warrior suki": "Suki",
    "kyoshi warrior suki": "Suki",

    "appa": "Appa",
    "sky bison": "Appa",
    "flying bison": "Appa",
    "bison": "Appa",

    "momo": "Momo",
    "winged lemur": "Momo",
    "lemur": "Momo",

    # --- Fire Nation / antagonists / allies ---
    "zuko": "Zuko",
    "prince zuko": "Zuko",
    "the banished prince": "Zuko",
    "banished prince": "Zuko",
    "the blue spirit": "Zuko",
    "blue spirit": "Zuko",
    "zuzu": "Zuko",
    "fire lord zuko": "Zuko",

    "iroh": "Iroh",
    "uncle": "Iroh",
    "uncle iroh": "Iroh",
    "general iroh": "Iroh",
    "dragon of the west": "Iroh",
    "the dragon of the west": "Iroh",
    "mushi": "Iroh",
    "tea guy": "Iroh",
    "jasmine dragon owner": "Iroh",

    "azula": "Azula",
    "princess azula": "Azula",
    "the princess": "Azula",
    "fire princess": "Azula",

    "ozai": "Ozai",
    "fire lord": "Ozai",
    "the fire lord": "Ozai",
    "fire lord ozai": "Ozai",
    "phoenix king": "Ozai",
    "phoenix king ozai": "Ozai",

    "zhao": "Zhao",
    "admiral zhao": "Zhao",
    "commander zhao": "Zhao",
    "captain zhao": "Zhao",
    "zhao the conqueror": "Zhao",

    "mai": "Mai",
    "gloomy girl": "Mai",

    "ty lee": "Ty Lee",
    "circus girl": "Ty Lee",
    "acrobat": "Ty Lee",

    "combustion man": "Combustion Man",
    "sparky sparky boom man": "Combustion Man",
    "sparky-sparky boom man": "Combustion Man",
    "sparky sparky boom boom man": "Combustion Man",
    "ssbm": "Combustion Man",
    "sparky": "Combustion Man",

    "june": "June",
    "bounty hunter june": "June",

    # --- Earth Kingdom / Ba Sing Se / Omashu ---
    "king bumi": "Bumi",
    "bumi": "Bumi",

    "kuei": "Kuei",
    "earth king": "Kuei",
    "the earth king": "Kuei",
    "king kuei": "Kuei",

    "long feng": "Long Feng",
    "grand secretariat": "Long Feng",
    "grand-secretariat": "Long Feng",
    "head of the dai li": "Long Feng",
    "dai li head": "Long Feng",

    "jet": "Jet",
    "freedom fighter jet": "Jet",

    "smellerbee": "Smellerbee",
    "smeller bee": "Smellerbee",

    "longshot": "Longshot",
    "long shot": "Longshot",

    "the boulder": "The Boulder",
    "boulder": "The Boulder",

    "xin fu": "Xin Fu",
    "earth rumble promoter": "Xin Fu",

    "master yu": "Master Yu",
    "yu": "Master Yu",

    "mechanist": "The Mechanist",
    "the mechanist": "The Mechanist",

    "teo": "Teo",

    "tyro": "Tyro",
    "haru": "Haru",
    "haruu": "Haru",  # common misspelling

    # --- Water Tribe / North & South ---
    "yue": "Yue",
    "princess yue": "Yue",

    "pakku": "Pakku",
    "master pakku": "Pakku",

    "hakoda": "Hakoda",
    "chief hakoda": "Hakoda",

    "bato": "Bato",

    "hama": "Hama",
    "the puppetmaster": "Hama",
    "puppetmaster": "Hama",

    # --- Masters, mentors, avatars, spirits ---
    "piandao": "Piandao",
    "master piandao": "Piandao",

    "jeong jeong": "Jeong Jeong",
    "master jeong jeong": "Jeong Jeong",
    "the deserter": "Jeong Jeong",

    "guru pathik": "Guru Pathik",
    "pathik": "Guru Pathik",
    "guru": "Guru Pathik",

    "avatar roku": "Roku",
    "roku": "Roku",

    "avatar kyoshi": "Kyoshi",
    "kyoshi": "Kyoshi",

    "avatar yangchen": "Yangchen",
    "yangchen": "Yangchen",

    "sozin": "Sozin",
    "fire lord sozin": "Sozin",

    "azulon": "Azulon",
    "fire lord azulon": "Azulon",

    "ursa": "Ursa",
    "lady ursa": "Ursa",

    "monk gyatso": "Gyatso",
    "gyatso": "Gyatso",
    "master gyatso": "Gyatso",

    "wan shi tong": "Wan Shi Tong",
    "the knowledge spirit": "Wan Shi Tong",
    "knowledge spirit": "Wan Shi Tong",
    "he who knows ten thousand things": "Wan Shi Tong",

    "koh": "Koh",
    "face stealer": "Koh",
    "koh the face stealer": "Koh",
    "the face stealer": "Koh",

    "hei bai": "Hei Bai",
    "heibai": "Hei Bai",  # common squashed form

    "huu": "Huu",

    # --- Recurring civilians / iconic side characters ---
    "cabbage merchant": "Cabbage Merchant",
    "cabbage man": "Cabbage Merchant",
    "cabbage guy": "Cabbage Merchant",
    "my cabbages guy": "Cabbage Merchant",
}
double_character_names_map = {
    "Aang and Sokka": ['Aang', 'Sokka'],
    "Gyatso and Katara": ['Gyatso', 'Katara'],
    "Poi and Ping": ['Poi', 'Ping'],
    "Lo and Li": ['Lo', 'Li'],
    "Li and Lo": ['Li', 'Lo'],
    "Aang and Zuko": ['Aang', 'Zuko'],
    "Toph and Sokka": ['Toph', 'Sokka'],
    "Katara and Sokka": ['Katara', 'Sokka']
}


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
