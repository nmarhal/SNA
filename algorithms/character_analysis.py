from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.read_data import *


def analyze_full_script():
    full_script_data = get_x_mentions_y()
    important_characters(full_script_data)

def analyze_each_book():
    all_books = get_x_mentions_y_per_book()
    for book in all_books:
        important_characters(book)

def analyze_each_episode():
    all_episodes = get_x_mentions_y_per_episode()
    for episode in all_episodes:
        important_characters(episode)

def important_characters(data_frame: pd.DataFrame):
    analyzer = NetworkStatisticsAnalyzer(data_frame)
    centrality_measures = analyzer.get_centrality_scores()
    print(centrality_measures)
