from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.book_names import BOOK_NAMES
from model.episode_names import EPISODE_NAMES
from model.read_data import *

def _print_centrality_scores(centrality_dict: dict, title: str):
    sorted_characters = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
    print(f"\n{title}")
    for character, centrality in sorted_characters:
        print(f"  {character}: {centrality}")

def _print_analysis(section_type: str, section_number: int, data_frame: pd.DataFrame):
    analyzer = NetworkStatisticsAnalyzer(data_frame)
    centrality_measures = analyzer.get_centrality_scores()

    print(f"\n{'=' * 50}")
    if section_type == "book":
        section_name = BOOK_NAMES[section_number]
    elif section_type == "episode":
        section_name = EPISODE_NAMES[section_number]
    else:
        section_name = "Avatar: The Legend of Aang"
    print(f"{section_type.upper()} {section_number}: {section_name}")
    print(f"{'=' * 50}")

    _print_centrality_scores(centrality_measures.in_degree, "In-Degree Centrality")
    # _print_centrality_scores(centrality_measures.betweenness, "Betweenness Centrality")
    # _print_centrality_scores(centrality_measures.closeness, "Closeness Centrality")
    # _print_centrality_scores(centrality_measures.eigenvector, "Eigenvector Centrality")

def analyze_full_script():
    full_script_data = get_x_mentions_y()
    _print_analysis(section_type="series", section_number=1, data_frame=full_script_data)

def analyze_each_book():
    all_books = get_x_mentions_y_per_book()
    for book_number, book in enumerate(all_books, start=1):
        _print_analysis(section_type="book", section_number=book_number, data_frame=book)

def analyze_each_episode():
    all_episodes = get_x_mentions_y_per_episode()
    for episode_number, episode in enumerate(all_episodes, start=1):
        _print_analysis(section_type="episode", section_number=episode_number, data_frame=episode)
