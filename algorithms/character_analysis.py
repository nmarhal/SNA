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

def _get_combined_centralities(analyzer: NetworkStatisticsAnalyzer):
    centralities = analyzer.get_centrality_scores()
    in_degree = centralities.in_degree
    eigenvector = centralities.eigenvector
    betweenness = centralities.betweenness
    characters = in_degree.keys()
    combined_centralities = dict()
    for character in characters:
        character_in_degree = in_degree.get(character, 0)
        character_eigenvector = eigenvector.get(character, 0)
        character_betweenness = betweenness.get(character, 0)
        combined_centralities[character] = (character_in_degree, character_eigenvector, character_betweenness)
    return combined_centralities

def analyze_full_script_centralities():
    full_script_data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(full_script_data)
    combined_centralities = _get_combined_centralities(analyzer)
    heading = _get_heading(section_type="series", section_number=1)
    save_centralities_to_csv(centralities=combined_centralities, heading=heading)

def analyze_each_book_centralities():
    all_books = get_x_mentions_y_per_book()
    for book_number, book in enumerate(all_books, start=1):
        analyzer = NetworkStatisticsAnalyzer(book)
        combined_centralities = _get_combined_centralities(analyzer)
        heading = _get_heading(section_type="book", section_number=book_number)
        save_centralities_to_csv(centralities=combined_centralities, heading=heading)

def analyze_each_episode_centralities():
    all_episodes = get_x_mentions_y_per_episode()
    for episode_number, episode in enumerate(all_episodes, start=1):
        analyzer = NetworkStatisticsAnalyzer(episode)
        combined_centralities = _get_combined_centralities(analyzer)
        heading = _get_heading(section_type="episode", section_number=episode_number)
        save_centralities_to_csv(centralities=combined_centralities, heading=heading)

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
