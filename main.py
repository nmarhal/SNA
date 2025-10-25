from algorithms.character_analysis import *
from algorithms.egocentric_networks import *
from algorithms.graph_algorithms import *
from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.read_data import *
from view.visualize_graphs import *
from view.visualize_sentiment import *

def compute_network_statistics():
    data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(data)
    edges = analyzer.get_number_of_edges()
    vertices = analyzer.get_number_of_vertices()
    diameters = analyzer.get_diameters_of_strongly_connected_components()
    density = analyzer.get_density()
    weakly_connected_components_count = analyzer.get_weakly_connected_components_count()
    strongly_connected_components_count = analyzer.get_strongly_connected_components_count()

    # todo bar chart - key=number of in-degrees, value=proportion of vertices with this degree
    in_degree_distribution = analyzer.get_in_degree_distribution()
    # todo bar chart - key=number of out-degrees, value=proportion of vertices with this degree
    out_degree_distribution = analyzer.get_out_degree_distribution()
    centrality_scores = analyzer.get_centrality_scores()
    # todo write for each node in the graph (key=character, value=coefficient)
    clustering_coefficient = analyzer.get_clustering_coefficient()
    weakly_connected_components = analyzer.get_weakly_connected_components()
    strongly_connected_components = analyzer.get_strongly_connected_components()
    print(
        f"""
        === Network Statistics ===
        number of edges: {edges}
        number of vertices: {vertices}
        diameters: {diameters}
        density: {density}
        number of weakly-connected components: {weakly_connected_components_count}
        number of strongly-connected components: {strongly_connected_components_count}
        """
    )

def visualize_graphs():
    characters = get_characters()

    min_weight = 3
    min_degree = 1
    color_by = "origin"
    show_labels = True
    label_top_k = 20
    directed = True

    # Visualize and perform analysis on mentions data
    data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(data)
    betweenness_centrality_label_data = LabelData(
        label_name="Betweenness Centrality",
        character_name_to_metric=analyzer.get_centrality_scores().betweenness
    )
    in_degree_centrality_label_data = LabelData(
        label_name="In-Degree Centrality",
        character_name_to_metric=analyzer.get_centrality_scores().in_degree
    )
    out_degree_centrality_label_data = LabelData(
        label_name="Out-Degree Centrality",
        character_name_to_metric=analyzer.get_centrality_scores().out_degree
    )
    eigenvector_centrality_label_data = LabelData(
        label_name="Eigenvector Centrality",
        character_name_to_metric=analyzer.get_centrality_scores().eigenvector
    )
    closeness_centrality_label_data = LabelData(
        label_name="Closeness Centrality",
        character_name_to_metric=analyzer.get_centrality_scores().closeness
    )
    clustering_coefficient_label_data = LabelData(
        label_name="Clustering Coefficient",
        character_name_to_metric=analyzer.get_clustering_coefficient()
    )
    visualize_all_layouts(data,
                          characters,
                          # label_data=clustering_coefficient_label_data,
                          color_by=color_by,
                          min_weight=min_weight,
                          min_degree=min_degree,
                          show_labels=show_labels,
                          label_top_k=label_top_k,
                          directed=directed)
    # analyze_hits(data, "x_mentions_y")
    # analyze_pagerank(data, " x_mentions_y")

def run_cliques_homophily_bridges_analysis():
    data = get_x_mentions_y()
    character_data = get_characters()
    # cliques:
    n_biggest, all_cliques = analyze_cliques(data, "x_mentions_y")
    print(n_biggest)
    for x in all_cliques:
        if len(x) == n_biggest:
            print(x)
    # homophily:
    results_gender, results_bending, results_origin = analyze_homophily(data, character_data, "x_mentions_y")
    print(results_gender)
    print(results_bending)
    print(results_origin)
    # bridges:
    weak_articulation, strong_articulation, weak_bridges = analyze_bridges(data, reciprocal=True)
    print(sorted(weak_articulation))
    print(sorted(strong_articulation))
    print(weak_bridges)

def visualize_sentiment():
    data = get_x_speaks_to_y_sentiment()
    datapoints = plot_sentiment_by_episode(data, "aang", "katara")
    print(datapoints)

def partition_graph():
    data = get_x_mentions_y()
    g_communities, g_labels, l_communities, l_labels, le_communities, le_labels = analyse_partitioning(data)
    graph = build_undirected_weighted(data)
    visualize_partition(graph, labels=g_labels, min_comm_size=4, show_labels=True)

def analyze_ego_networks():
    egos = [
        "aang"
        # "zuko",
        # "katara",
        # "sokka",
        # "toph",
        # "jet",
        # "zhao"
        # "appa",
        # "momo"
    ]
    for ego in egos:
        min_weight = 10
        analyze_character_ego_network_per_book(ego)
        visualize_character_ego_networks_per_book(ego, min_weight=min_weight, save=True)

def main():
    # compute_network_statistics()
    # partition_graph()
    # analyze_full_script()
    # analyze_each_book()
    # analyze_each_episode()
    # visualize_graphs()
    # analyze_ego_networks()
    # analyze_clustering_full_script()
    # analyze_clustering_per_book()
    # analyze_clustering_per_episode()
    # visualize_character_ego_networks_per_book("katara", min_weight=2)
    analyze_full_script_centralities()
    analyze_each_book_centralities()
    analyze_each_episode_centralities()

    return

if __name__ == "__main__":
    main()
