from model.constants import *
from model.read_data import *


def cleanup_edges(data):
    characters = get_characters()
    valid = list(characters.get(COL_NAME))
    valid = [x.lower() for x in valid]
    out = data[data[COL_X].isin(valid) & data[COL_Y].isin(valid)].reset_index(drop=True)
    return out


def weigh_rows(data):
    weighted = (
        data.value_counts([COL_X, COL_Y])
        .rename(WEIGHT)
        .reset_index()
    )
    return weighted


def lower_dataset(data):
    data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    return data
