from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.book_names import BOOK_NAMES
from model.episode_names import EPISODE_NAMES
from model.read_data import *

from view.create_tables import *

def _get_characters_sorted_by_centrality_scores(centrality_dict: dict):
    return sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)

def _print_centrality_scores(centrality_dict: dict, title: str):
    sorted_characters = _get_characters_sorted_by_centrality_scores(centrality_dict)
    print(f"\n{title}")
    for character, centrality in sorted_characters:
        print(f"  {character}: {centrality}")

def _get_heading(section_type: str, section_number: int):
    if section_type == "book":
        section_name = BOOK_NAMES[section_number]
    elif section_type == "episode":
        section_name = EPISODE_NAMES[section_number]
    else:
        return "Avatar: The Legend of Aang"
    return f"{section_type.upper()} {section_number}: {section_name}"

def _print_centrality_analysis(section_type: str, section_number: int, analyzer: NetworkStatisticsAnalyzer):
    centrality_measures = analyzer.get_centrality_scores()

    print(f"\n{'=' * 50}")
    print(_get_heading(section_type, section_number))
    print(f"{'=' * 50}")

    _print_centrality_scores(centrality_measures.in_degree, "In-Degree Centrality")
    # _print_centrality_scores(centrality_measures.betweenness, "Betweenness Centrality")
    # _print_centrality_scores(centrality_measures.closeness, "Closeness Centrality")
    # _print_centrality_scores(centrality_measures.eigenvector, "Eigenvector Centrality")


def analyze_full_script():
    full_script_data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(full_script_data)
    _print_centrality_analysis(section_type="series", section_number=1, analyzer=analyzer)

def analyze_each_book():
    all_books = get_x_mentions_y_per_book()
    for book_number, book in enumerate(all_books, start=1):
        analyzer = NetworkStatisticsAnalyzer(book)
        _print_centrality_analysis(section_type="book", section_number=book_number, analyzer=analyzer)


def analyze_each_episode():
    all_episodes = get_x_mentions_y_per_episode()
    for episode_number, episode in enumerate(all_episodes, start=1):
        analyzer = NetworkStatisticsAnalyzer(episode)
        _print_centrality_analysis(section_type="episode", section_number=episode_number, analyzer=analyzer)

def analyze_clustering_full_script():
    full_script_data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(full_script_data)
    clustering_coefficient = analyzer.get_clustering_coefficient()
    average_clustering = analyzer.get_average_clustering()
    transitivity = analyzer.get_transitivity()
    heading = _get_heading(section_type="series", section_number=1)
    save_clustering_coefficient_to_csv(clustering_coefficient, average_clustering, transitivity, heading)

def analyze_clustering_per_book():
    all_books = get_x_mentions_y_per_book()
    for book_number, book in enumerate(all_books, start=1):
        analyzer = NetworkStatisticsAnalyzer(book)
        heading = _get_heading(section_type="book", section_number=book_number)
        clustering_coefficient = analyzer.get_clustering_coefficient()
        average_clustering = analyzer.get_average_clustering()
        transitivity = analyzer.get_transitivity()
        save_clustering_coefficient_to_csv(clustering_coefficient, average_clustering, transitivity, heading)

def analyze_clustering_per_episode():
    all_episodes = get_x_mentions_y_per_episode()
    for episode_number, episode in enumerate(all_episodes, start=1):
        analyzer = NetworkStatisticsAnalyzer(episode)
        heading = _get_heading(section_type="episode", section_number=episode_number)
        clustering_coefficient = analyzer.get_clustering_coefficient()
        average_clustering = analyzer.get_average_clustering()
        transitivity = analyzer.get_transitivity()
        save_clustering_coefficient_to_csv(clustering_coefficient, average_clustering, transitivity, heading)
