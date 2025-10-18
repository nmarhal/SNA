from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.read_data import get_x_mentions_y

full_script_data = get_x_mentions_y()


def analyze_full_script():
    analyzer = NetworkStatisticsAnalyzer(full_script_data)


def analyze_each_book():
    # full_script_data[full_script_data[]]
    pass
