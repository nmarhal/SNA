import re
from functools import lru_cache

from model.character_aliases import *
from model.constants import *
from model.read_data import *


@lru_cache(maxsize=1024)
def _pattern_for(name: str) -> re.Pattern:
    parts = re.split(r'\s+', name.strip())
    # If you want to allow punctuation between words, use r'\W+' instead of r'\s+'
    pat = r'(?<!\w)' + r'\s+'.join(map(re.escape, parts)) + r'(?!\w)'
    return re.compile(pat, re.IGNORECASE)


def has_name(line: str, character_name: str) -> bool:
    return bool(_pattern_for(character_name).search(line))


def get_line_without_square_brackets(full_line: str):
    return re.sub(r"\[.*?\]", "", full_line)


def get_valid_names():
    """
    :return:
    name_set : set
        set of all character names that might appear in the script, including aliases
    name_map : dict
        dict that maps all character names in name_set to their official character names
    """
    official_character_names = get_characters()[COL_NAME]
    name_map = alias_map.copy()
    for official_character_name in official_character_names:
        official_character_name = official_character_name.lower()
        name_map[official_character_name] = official_character_name
    name_list = sorted(list(name_map.keys()))
    for i in range(len(name_list)):
        name_list[i] = name_list[i].lower()
    name_set = sorted(set(name_list))
    return name_set, name_map


