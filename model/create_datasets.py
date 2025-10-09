import pandas as pd
import re
from functools import lru_cache

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

    "Wu": "Aunt Wu",
    "Wu": "aunt wu",
    "Wu": "wu",
    "Wu": "aunt Wu",

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

@lru_cache(maxsize=1024)
def _pattern_for(name: str) -> re.Pattern:
    parts = re.split(r'\s+', name.strip())
    # If you want to allow punctuation between words, use r'\W+' instead of r'\s+'
    pat = r'(?<!\w)' + r'\s+'.join(map(re.escape, parts)) + r'(?!\w)'
    return re.compile(pat, re.IGNORECASE)

def has_name(line: str, character_name: str) -> bool:
    return bool(_pattern_for(character_name).search(line))

def get_unique_characters():
    script = get_script()
    unique_characters = script.get("Character").dropna().unique()
    unique_characters = list(unique_characters)
    for character in unique_characters:
        if len(character.split(" and ")) > 1:
            unique_characters.remove(character)
    unique_characters.remove("Katara and Sokka")
    return unique_characters

def x_speaks_before_y():
    """
    Simple connection where a character x spoke their line before character y
    Gives a rough "x speaks to y" relationship network, but will have false edges
    """
    script = get_script()
    previous_character = None
    x_speaks_to_y = [] # we will add edges to this list
    for index, row in script.iterrows():
        character = row["Character"]
        if previous_character is None: # there is no x, go to next line
            if pd.isna(character):
                previous_character = None
            else:
                previous_character = character
            continue
        if pd.isna(character): # there is no y, go to next line
            previous_character = None
            continue
        # Sometimes there are characters in the script called "Sokka and Katara" in this case we awant to
        # split these names and add an edge for "Sokka" and an edge for "Katara"
        x = double_character_names_map[character] if character in double_character_names_map else [character]
        y = double_character_names_map[previous_character] if previous_character in double_character_names_map else [previous_character]
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
    # we load the script
    script = get_script()
    # we create a dict of all character names to their official names
    official_character_names = get_accepted_character_names()
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
        character = row["Character"]
        line = row["script"]
        match = False
        line = re.sub(r"\[.*?\]", "", line)
        # get the character(s) that is speaking
        if pd.isna(character): # characterless line
            continue
        x = double_character_names_map[character] if character in double_character_names_map else [character]
        # get the character(s) mentioned in the line
        for character_name in name_set:
            character_name = character_name.lower()
            if has_name(line=line, character_name=character_name):
                for i in x:
                    i = i.lower()
                    valid_name = name_map[character_name].lower()
                    if match:
                        print(f"{i}: [{character_name}, {valid_name}] {line}")
                    x_mentions_y.append([i, valid_name])
    return pd.DataFrame(x_mentions_y, columns=["x", "y"])

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
    weighted.to_csv("model/data/x_speaks_to_y.csv", index=False)

    data = x_mentions_y()
    data = cleanup_edges(data)
    weighted = weigh_rows(data)
    weighted.to_csv("model/data/x_mentions_y.csv", index=False)

    # data = get_characters()
    # data = lower_dataset(data)
    # data.to_csv("model/data/characters.csv", index=False)
    return

if __name__ == "__main__":
    main()