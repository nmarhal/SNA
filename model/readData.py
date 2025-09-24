"""
Reads data from the csv files and annotates characters with House, Culture, Gender.
Efficient API usage: one character request per unique normalized name (cached),
and one request per unique house URL (cached).
"""

import re
import pandas as pd
import requests
from functools import lru_cache
from urllib.parse import quote

count = 0  # optional progress counter

# --- helpers -----------------------------------------------------------------

def normalize_person_name(raw: str) -> str:
    """
    Normalize a raw name into the exact shape expected by the API:
    - strip whitespace
    - drop parentheticals, e.g. "(Maester Aemon)"
    - replace hyphens with spaces
    - collapse repeated spaces
    - drop a trailing 'Targaryen' *only if it appears at the end*
      (so 'Aegon-I-Targaryen' -> 'Aegon I'; 'Daenerys-Targaryen' -> 'Daenerys')
    """
    s = raw.strip()
    s = re.sub(r"\s*\([^)]*\)\s*", "", s)   # drop parentheticals
    s = s.replace("-", " ")                 # hyphens -> spaces
    s = re.sub(r"\s+", " ", s)              # collapse spaces
    s = re.sub(r"\bTargaryen$", "", s).strip()  # drop trailing 'Targaryen'
    return s

def last_token(name: str) -> str:
    toks = name.split()
    return toks[-1] if toks else ""

def canonicalize_house(hname: str) -> tuple[str, str]:
    """
    Normalize a house name and return (base, family) where:
    - base   = 'House Targaryen'
    - family = 'Targaryen'
    """
    if not hname:
        return "", ""
    base = re.match(r"^(House\s+[A-Za-z' -]+)", hname)
    base = base.group(1) if base else hname
    family = base.replace("House", "").strip()
    return base, family

# Families we’re comfortable inferring by surname
KNOWN_FAMILIES = {
    "Stark","Lannister","Targaryen","Baratheon","Tyrell","Greyjoy","Arryn","Martell","Tully",
    "Bolton","Frey","Mormont","Clegane","Payne","Hightower","Oakheart","Dayne","Tarly","Vance",
    "Piper","Corbray","Lefford","Karstark","Royce","Swann","Tarth","Manderly",
    "Hornwood","Bracken","Selmy","Seaworth","Celtigar","Velaryon"
}

# Explicit culture overrides (use sparingly; only when API lacks culture)
CULTURE_OVERRIDES = {
    "Aggo": "Dothraki",
    "Jhogo": "Dothraki",
    "Qotho": "Dothraki",
    "Rakharo": "Dothraki",
    # add more as you encounter them
}

TITLE_GENDER_HINTS = [
    (r"^\s*Ser\b", "Male"),
    (r"^\s*Lord\b", "Male"),
    (r"^\s*Prince\b", "Male"),
    (r"^\s*King\b", "Male"),
    (r"^\s*Maester\b", "Male"),
    (r"^\s*Brother\b", "Male"),
    (r"^\s*Septon\b", "Male"),
    (r"^\s*Lady\b", "Female"),
    (r"^\s*Princess\b", "Female"),
    (r"^\s*Queen\b", "Female"),
    (r"^\s*Septa\b", "Female"),
    (r"^\s*Sister\b", "Female"),
]

# --- API access (cached) -----------------------------------------------------

@lru_cache(maxsize=4096)
def fetch_character_record(norm_name: str) -> dict:
    """
    Exact-name query only to avoid alias cross-talk.
    Returns the first matching character object or {} if none.
    """
    url = f"https://www.anapioficeandfire.com/api/characters?name={quote(norm_name)}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    items = r.json()
    return items[0] if items else {}

@lru_cache(maxsize=8192)
def fetch_house_name(h_url: str) -> str:
    """
    Cache each house URL -> 'House X' base name. One request per unique URL per run.
    """
    try:
        h = requests.get(h_url, timeout=15).json().get("name", "")
        base, _ = canonicalize_house(h)
        return base
    except Exception:
        return ""

def resolve_character(norm_name: str) -> dict:
    """
    Single-shot resolver using ONE character fetch, then cached house lookups.
    Returns dict with:
      {
        'houses': [ 'House X', ... ],
        'culture': 'Dothraki' | '' ,
        'gender': 'Male' | 'Female' | ''
      }
    """
    rec = fetch_character_record(norm_name)
    if not rec:
        return {"houses": [], "culture": "", "gender": ""}

    # Houses via allegiance URLs (each URL is cached)
    houses = []
    for h_url in rec.get("allegiances", []):
        base = fetch_house_name(h_url)
        if base:
            houses.append(base)

    # Culture & Gender from the character record
    culture = normalize_culture(rec.get("culture", ""))
    gender = (rec.get("gender", "") or "").strip().title()
    gender = gender if gender in {"Male", "Female"} else ""

    return {"houses": houses, "culture": culture, "gender": gender}

# --- inferences --------------------------------------------------------------

def infer_house_from_name(raw: str) -> str:
    name = normalize_person_name(raw)
    fam = last_token(name)
    if fam in KNOWN_FAMILIES:
        return f"House {fam}"
    return ""  # unknown / non-house

def normalize_culture(s: str) -> str:
    s = (s or "").strip()
    # Keep original words but title-case common ASCII letters.
    return s.title() if s else ""

def culture_from_api(norm_name: str) -> str:
    return resolve_character(norm_name)["culture"]

def gender_from_api(norm_name: str) -> str:
    return resolve_character(norm_name)["gender"]

def infer_gender_from_title(raw: str) -> str:
    for pattern, g in TITLE_GENDER_HINTS:
        if re.search(pattern, raw, flags=re.IGNORECASE):
            return g
    return ""

# --- per-field resolvers (house/culture/gender) ------------------------------

def house_for_source(raw: str) -> str:
    """
    Returns a semicolon-separated list of houses (or empty string).
    Never returns culture strings.
    """
    norm = normalize_person_name(raw)
    fam = last_token(norm)

    try:
        api_houses = resolve_character(norm)["houses"]
    except Exception:
        api_houses = []

    kept = []
    for h in api_houses:
        base, hfam = canonicalize_house(h)
        if fam and hfam == fam:  # surname guard
            kept.append(base)

    # Fallback to surname inference if API gave nothing that matches surname
    if not kept:
        fb = infer_house_from_name(raw)
        if fb:
            kept = [fb]

    global count
    count += 1
    print(f"{count}\tfinished {raw} [HOUSE]:\t{'; '.join(sorted(set(kept)))}")
    return "; ".join(sorted(set(kept)))

def culture_for_source(raw: str) -> str:
    """
    Prefer API culture; otherwise use explicit overrides; otherwise blank.
    """
    norm = normalize_person_name(raw)

    # 1) API
    try:
        c = culture_from_api(norm)
    except Exception:
        c = ""

    # 2) Overrides (only if API is blank)
    if not c and raw in CULTURE_OVERRIDES:
        c = CULTURE_OVERRIDES[raw]
    global count
    count += 1
    print(f"{count}\t\t{raw} [CULTURE]:\t{c}")
    return c

def gender_for_source(raw: str) -> str:
    """
    Prefer API gender; fallback to title-based inference; otherwise blank.
    """
    norm = normalize_person_name(raw)

    # 1) API
    try:
        g = gender_from_api(norm)
    except Exception:
        g = ""

    # 2) Minimal heuristic by honorific/title
    if not g:
        g = infer_gender_from_title(raw)
    global count
    count += 1
    print(f"{count}\t{raw} [GENDER]:\t{g}")
    return g

# --- dataframe helpers -------------------------------------------------------

def annotate_sources_with_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Backwards-compatible: builds a mapping only for unique values in df['Source'].
    Returns a dataframe with columns: Source, House, Culture, Gender
    """
    uniq = pd.Series(df["Source"].unique(), name="Source")
    mapping = pd.DataFrame({"Source": uniq})
    global count
    mapping["House"] = mapping["Source"].apply(house_for_source)
    count = 0
    mapping["Culture"] = mapping["Source"].apply(culture_for_source)
    count = 0
    mapping["Gender"] = mapping["Source"].apply(gender_for_source)
    return mapping

def annotate_characters_with_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preferred: builds a mapping for ALL unique characters from both Source and Target.
    Returns a dataframe with columns: Character, House, Culture, Gender
    """
    uniq = pd.Series(pd.concat([df["Source"], df["Target"]]).unique(), name="Character")
    mapping = pd.DataFrame({"Character": uniq})
    mapping["House"] = mapping["Character"].apply(house_for_source)
    mapping["Culture"] = mapping["Character"].apply(culture_for_source)
    mapping["Gender"] = mapping["Character"].apply(gender_for_source)
    return mapping

# --- CSV loaders -------------------------------------------------------------

def get_all_data() -> pd.DataFrame:
    book1 = pd.read_csv('Dataset/annotated_book1.csv')
    book2 = pd.read_csv('Dataset/book2.csv')
    book3 = pd.read_csv('Dataset/book3.csv')
    book4 = pd.read_csv('Dataset/book4.csv')
    book5 = pd.read_csv('Dataset/book5.csv')
    result = [book1, book2, book3, book4, book5]
    result = pd.concat(result, ignore_index=True)
    return result

def get_book_1() -> pd.DataFrame: return pd.read_csv('Dataset/book1.csv')
def get_book_2() -> pd.DataFrame: return pd.read_csv('Dataset/book2.csv')
def get_book_3() -> pd.DataFrame: return pd.read_csv('Dataset/book3.csv')
def get_book_4() -> pd.DataFrame: return pd.read_csv('Dataset/book4.csv')
def get_book_5() -> pd.DataFrame: return pd.read_csv('Dataset/book5.csv')

def get_characters_1() -> pd.DataFrame: return pd.read_csv('Dataset/characters_book1.csv')
