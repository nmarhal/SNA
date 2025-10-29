from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.book_names import BOOK_NAMES
from model.entities.centrality_scores import CentralityScores
from model.episode_names import EPISODE_NAMES
from model.read_data import *

from view.create_tables import *
from view.centrality_progression_plotter import MetricsProgressionPlotter

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

def _get_top_centrality(centrality_dict: dict, take_first: int = None):
    if take_first is not None:
        sorted_items = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:take_first])
    return centrality_dict

def _save_centralities_to_csv_for_section(centralities: CentralityScores, section_type: str, section_number: int):
    heading = _get_heading(section_type=section_type, section_number=section_number)
    in_degree = _get_top_centrality(centralities.in_degree, take_first=10)
    eigenvector = _get_top_centrality(centralities.eigenvector, take_first=10)
    betweenness = _get_top_centrality(centralities.betweenness, take_first=10)

    save_centrality_to_csv(in_degree, "in-degree", heading)
    save_centrality_to_csv(eigenvector, "eigenvector", heading)
    save_centrality_to_csv(betweenness, "betweenness", heading)

def analyze_full_script_centralities():
    full_script_data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(full_script_data)
    centralities = analyzer.get_centrality_scores()
    heading = _get_heading(section_type="series", section_number=1)

    in_degree = _get_top_centrality(centralities.in_degree, take_first=10)
    eigenvector = _get_top_centrality(centralities.eigenvector, take_first=10)
    betweenness = _get_top_centrality(centralities.betweenness, take_first=10)

    save_centrality_to_csv(in_degree, "in-degree", heading)
    save_centrality_to_csv(eigenvector, "eigenvector", heading)
    save_centrality_to_csv(betweenness, "betweenness", heading)

def analyze_each_book_centralities():
    all_books = get_x_mentions_y_per_book()
    in_degree_plotter = MetricsProgressionPlotter(metrics_name="in-degree centrality", section_type="book", folder_name="centralities")
    eigenvector_plotter = MetricsProgressionPlotter(metrics_name="eigenvector centrality", section_type="book", folder_name="centralities")
    betweenness_plotter = MetricsProgressionPlotter(metrics_name="betweenness centrality", section_type="book", folder_name="centralities")
    for book_number, book in enumerate(all_books, start=1):
        analyzer = NetworkStatisticsAnalyzer(book)
        centralities = analyzer.get_centrality_scores()

        _save_centralities_to_csv_for_section(centralities, section_type="book", section_number=book_number)

        in_degree_plotter.add_data_point(centralities.in_degree)
        eigenvector_plotter.add_data_point(centralities.eigenvector)
        betweenness_plotter.add_data_point(centralities.betweenness)
    in_degree_plotter.draw()
    eigenvector_plotter.draw()
    betweenness_plotter.draw()

def analyze_each_episode_centralities():
    all_episodes = get_x_mentions_y_per_episode()
    in_degree_plotter = MetricsProgressionPlotter(metrics_name="in-degree centrality", section_type="episode", folder_name="centralities", top_n=20)
    eigenvector_plotter = MetricsProgressionPlotter(metrics_name="eigenvector centrality", section_type="episode", folder_name="centralities", top_n=20)
    betweenness_plotter = MetricsProgressionPlotter(metrics_name="betweenness centrality", section_type="episode", folder_name="centralities", top_n=20)
    for episode_number, episode in enumerate(all_episodes, start=1):
        analyzer = NetworkStatisticsAnalyzer(episode)
        centralities = analyzer.get_centrality_scores()

        _save_centralities_to_csv_for_section(centralities, section_type="episode", section_number=episode_number)

        in_degree_plotter.add_data_point(centralities.in_degree)
        eigenvector_plotter.add_data_point(centralities.eigenvector)
        betweenness_plotter.add_data_point(centralities.betweenness)
    characters = ["zuko", "aang"]
    in_degree_plotter.draw(key_filter=characters, trend_lines=characters)
    eigenvector_plotter.draw(key_filter=characters, trend_lines=characters)
    betweenness_plotter.draw(key_filter=characters, trend_lines=characters)

def analyze_clustering_full_script():
    full_script_data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(full_script_data)
    clustering_coefficient = analyzer.get_clustering_coefficient()
    average_clustering = analyzer.get_average_clustering()
    transitivity = analyzer.get_transitivity()
    print("full script average clustering: ", f"{average_clustering:.3f}")
    print("full script transitivity: ", f"{transitivity:.3f}")
    heading = _get_heading(section_type="series", section_number=1)
    save_clustering_coefficient_to_csv(clustering_coefficient, heading)

def analyze_clustering_per_book():
    all_books = get_x_mentions_y_per_book()
    clustering_plotter = MetricsProgressionPlotter(metrics_name="clustering coefficient", section_type="book", folder_name="clustering")
    for book_number, book in enumerate(all_books, start=1):
        analyzer = NetworkStatisticsAnalyzer(book)
        heading = _get_heading(section_type="book", section_number=book_number)
        clustering_coefficient = analyzer.get_clustering_coefficient()
        average_clustering = analyzer.get_average_clustering()
        transitivity = analyzer.get_transitivity()
        clustering_plotter.add_data_point_with_kwargs(average_clustering=average_clustering, transitivity=transitivity)
    clustering_plotter.draw(trend_lines=["average_clustering", "transitivity"])

def analyze_clustering_per_episode():
    all_episodes = get_x_mentions_y_per_episode()
    clustering_plotter = MetricsProgressionPlotter(metrics_name="clustering coefficient", section_type="episode", folder_name="clustering")
    episode_to_average_clustering = {}
    episode_to_transitivity = {}
    for episode_number, episode in enumerate(all_episodes, start=1):
        analyzer = NetworkStatisticsAnalyzer(episode)
        heading = _get_heading(section_type="episode", section_number=episode_number)
        average_clustering = analyzer.get_average_clustering()
        transitivity = analyzer.get_transitivity()
        clustering_plotter.add_data_point_with_kwargs(average_clustering=average_clustering, transitivity=transitivity)
        episode_to_average_clustering[episode_number] = average_clustering
        episode_to_transitivity[episode_number] = transitivity
    clustering_plotter.draw(trend_lines=["average_clustering", "transitivity"])
    sorted_episodes = sorted(episode_to_average_clustering.items(), key=lambda x: x[1], reverse=True)
    print("sorted episodes by average clustering: ", sorted_episodes)
    sorted_episodes = sorted(episode_to_transitivity.items(), key=lambda x: x[1], reverse=True)
    print("sorted episodes by transitivity: ", sorted_episodes)
