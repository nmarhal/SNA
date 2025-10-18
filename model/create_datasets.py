from algorithms.sentiment_analysis import *
from model.entities.x_mentions_y_row_data import XMentionsYRowData
from model.utils.dataset_utils import *
from model.utils.utils import *
from read_data import *

SENTIMENT_COLUMNS = [
    COL_X,
    COL_Y,
    SENTIMENT_NEG,
    SENTIMENT_NEU,
    SENTIMENT_POS,
    SENTIMENT_COMPOUND,
    COL_TOTAL_EPISODE_NUMBER,
    COL_SCRIPT
]

def x_speaks_before_y():
    """
    Simple connection where a character x spoke their line before character y
    Gives a rough "x speaks to y" relationship network, but will have false edges
    """
    script = get_script()
    previous_character = None
    x_speaks_to_y = []  # we will add edges to this list
    for index, row in script.iterrows():
        character = row[COL_CHARACTER]
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
    return pd.DataFrame(x_speaks_to_y, columns=[COL_X, COL_Y])


def x_mentions_y_row_generator():
    """
    x mentions y in a line, uses the official character names as well as many aliases as I could find specified
    in the alias map
    """
    script = get_script()
    # we retrieve all possible names in name_set and a dict to get their official name_map
    name_set, name_map = get_valid_names()
    # iterate over all lines in the script
    for index, row in script.iterrows():
        speakers = row[COL_CHARACTER]
        full_line = row[COL_SCRIPT]
        book = row[COL_BOOK]
        episode = row[COL_TOTAL_EPISODE_NUMBER]
        line_without_square_brackets = get_line_without_square_brackets(full_line)
        # get the character(s) that is speaking, ignoring the narrator
        if pd.isna(speakers):
            continue
        speakers = double_character_names_map[speakers] if speakers in double_character_names_map else [speakers]
        # get the character(s) mentioned in the line
        addressed_characters_saved = []
        for character_addressed in name_set:
            character_addressed = character_addressed.lower()
            if has_name(line=line_without_square_brackets, character_name=character_addressed):
                for speaker in speakers:
                    speaker = speaker.lower()
                    character_addressed = name_map[character_addressed].lower()
                    if character_addressed in addressed_characters_saved:
                        continue
                    addressed_characters_saved.append(character_addressed)
                    yield XMentionsYRowData(speaker, character_addressed, book, episode, full_line)


def x_mentions_y():
    x_mentions_y_rows = []
    row_generator = x_mentions_y_row_generator()
    for row in row_generator:
        x_mentions_y_rows.append([row.speaker, row.character_addressed])
    x_mentions_y_data_frame = pd.DataFrame(x_mentions_y_rows, columns=[COL_X, COL_Y])
    return x_mentions_y_data_frame


def x_mentions_y_with_sentiment():
    x_mentions_y_with_sentiment_rows = []
    row_generator = x_mentions_y_row_generator()
    for row in row_generator:
        sentiment = get_sentiment(row.full_line)
        x_mentions_y_with_sentiment_rows.append([
            row.speaker,
            row.character_addressed,
            sentiment[SENTIMENT_NEG],
            sentiment[SENTIMENT_NEU],
            sentiment[SENTIMENT_POS],
            sentiment[SENTIMENT_COMPOUND],
            row.episode,
            row.full_line
        ])
    x_mentions_y_with_sentiment_data_frame = pd.DataFrame(
        x_mentions_y_with_sentiment_rows,
        columns=SENTIMENT_COLUMNS
    )
    return x_mentions_y_with_sentiment_data_frame


def x_mentions_y_per(group_name: str):
    section_data_frames = {}
    x_mentions_y_rows = []
    current_section = 1
    row_generator = x_mentions_y_row_generator()

    def add_current_section_data_frame():
        section_data_frame = pd.DataFrame(x_mentions_y_rows, columns=[COL_X, COL_Y])
        section_data_frames[current_section] = section_data_frame

    for row in row_generator:
        row_section = row[group_name]

        def is_section_changed():
            return current_section != row_section

        x_mentions_y_rows.append([row.speaker, row.character_addressed])
        if is_section_changed():
            add_current_section_data_frame()
            current_section = row_section
            x_mentions_y_rows = []

    add_current_section_data_frame()
    return section_data_frames


def compute_x_mentions_y_weighted_data(data: pd.DataFrame):
    cleaned_up_edges = cleanup_edges(data)
    weighted_rows = weigh_rows(cleaned_up_edges)
    return weighted_rows


def main():
    # data = x_speaks_before_y()
    # data = cleanup_edges(data)
    # weighted = weigh_rows(data)
    # # weighted.to_csv("./data/x_speaks_to_y.csv", index=False)
    # # uncomment this if my code with ./data does not work
    # weighted.to_csv("model/data/x_speaks_to_y.csv", index=False)

    # data = x_mentions_y()
    # data_with_sentiment = x_mentions_y_with_sentiment()
    # data = cleanup_edges(data)
    # data_with_sentiment = cleanup_edges(data_with_sentiment)
    # weighted = weigh_rows(data)
    # weighted.to_csv("./data/x_mentions_y.csv", index=False)
    # data_with_sentiment.to_csv("./data/x_mentions_y_with_sentiment.csv", index=False)
    # # uncomment this if my code with ./data does not work
    # weighted.to_csv("./data/x_mentions_y.csv", index=False)
    # data_with_sentiment.to_csv("./data/x_mentions_y_with_sentiment_and_line.csv", index=False)

    data_per_episode = x_mentions_y_per("episode")
    for episode, data_frame in data_per_episode.items():
        weighted_rows = compute_x_mentions_y_weighted_data(data_frame)
        weighted_rows.to_csv(f"./data/episodes/ep_{episode}_x_mentions_y.csv", index=False)

    data_per_book = x_mentions_y_per("book")
    for book, data_frame in data_per_book.items():
        weighted_rows = compute_x_mentions_y_weighted_data(data_frame)
        weighted_rows.to_csv(f"./data/books/book_{book}_x_mentions_y.csv", index=False)

    return


if __name__ == "__main__":
    main()
