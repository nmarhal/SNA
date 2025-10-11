from algorithms.network_statistics import NetworkStatisticsAnalyzer
from view.visualize_graphs import *
from model.read_data import *
from algorithms.graph_algorithms import *

def visualize_graphs():
    characters = get_characters()

    min_weight = 10
    min_degree = 1
    color_by = "origin"
    show_labels = True
    label_top_k = 20
    directed = True

    # Visualize and perform analysis on mentions data
    data = get_x_mentions_y()
    # todo: visualize analyzer data
    analyzer = NetworkStatisticsAnalyzer(data)
    edges = analyzer.get_number_of_edges()
    vertices = analyzer.get_number_of_vertices()
    in_degree_distribution = analyzer.get_in_degree_distribution()
    out_degree_distribution = analyzer.get_out_degree_distribution()
    centrality_scores = analyzer.get_centrality_scores()
    visualize_all_layouts(data,
                          characters,
                          color_by=color_by,
                          min_weight=min_weight,
                          min_degree=min_degree,
                          show_labels=show_labels,
                          label_top_k=label_top_k,
                          directed=directed)
    analyze_hits(data, "x_mentions_y")
    analyze_pagerank(data, " x_mentions_y")

    # Visualize and perform analysis on speaks_to data
    data = get_x_speaks_to_y()
    visualize_all_layouts(data,
                          characters,
                          color_by=color_by,
                          min_weight=min_weight,
                          min_degree=min_degree,
                          show_labels=show_labels,
                          label_top_k=label_top_k,
                          directed=directed)
    analyze_hits(data, "x_speaks_to_y")
    analyze_pagerank(data, "x_speaks_to_y")

def run_cliques_homophily_bridges_analysis():
    data = get_x_mentions_y()
    character_data = get_characters()
    n_biggest, all_cliques = analyze_cliques(data, "x_mentions_y")
    print(n_biggest)
    for x in all_cliques:
        if len(x) == n_biggest:
            print(x)
    results_gender, results_bending, results_origin = analyze_homophily(data, character_data, "x_mentions_y")
    print(results_gender)
    print(results_bending)
    print(results_origin)


def main():
    run_cliques_homophily_bridges_analysis()
    return


if __name__ == "__main__":
    main()