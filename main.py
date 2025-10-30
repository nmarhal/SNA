from algorithms.character_analysis import *
from algorithms.egocentric_networks import *
from algorithms.graph_algorithms import *
from algorithms.network_statistics import NetworkStatisticsAnalyzer
from model.read_data import *
from view.degree_distribution import plot_degree_distribution
from view.visualize_graphs import *
from view.visualize_sentiment import *
from view.partition_histograms import *
import os

def compute_network_statistics():
    os.makedirs("results/degree", exist_ok=True)
    data = get_x_mentions_y()
    analyzer = NetworkStatisticsAnalyzer(data)
    edges = analyzer.get_number_of_edges()
    vertices = analyzer.get_number_of_vertices()
    diameters = analyzer.get_diameters_of_strongly_connected_components()
    density = analyzer.get_density()
    weakly_connected_components_count = analyzer.get_weakly_connected_components_count()
    strongly_connected_components_count = analyzer.get_strongly_connected_components_count()

    in_degree_distribution = analyzer.get_in_degree_distribution()
    out_degree_distribution = analyzer.get_out_degree_distribution()
    weakly_connected_components_size_counts = analyzer.get_weakly_connected_components_size_counts()
    strongly_connected_components_size_counts = analyzer.get_strongly_connected_components_size_counts()
    
    in_degree, _ = plot_degree_distribution(in_degree_distribution, title="In-Degree Distribution", xlabel="In-Degree")
    out_degree, _ = plot_degree_distribution(out_degree_distribution, title="Out-Degree Distribution", xlabel="Out-Degree")
    in_degree.savefig("results/degree/in_degree_distribution.png")
    out_degree.savefig("results/degree/out_degree_distribution.png")
    
    print(
        f"""
        === Network Statistics ===
        number of edges: {edges}
        number of vertices: {vertices}
        diameters: {diameters}
        density: {density}
        number of weakly-connected components: {weakly_connected_components_count}
        number of strongly-connected components: {strongly_connected_components_count}
        weakly connected components size distribution: {dict(sorted(weakly_connected_components_size_counts.items()))}
        strongly connected components size distribution: {dict(sorted(strongly_connected_components_size_counts.items()))}
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

    data = get_x_mentions_y()
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

def run_cliques_homophily_bridges_analysis():
    data = get_x_mentions_y()
    character_data = get_characters()
    # cliques:
    n_biggest, all_cliques = analyze_cliques(data, "x_mentions_y")
    print("""
    ======================================================================
    Homophily, Cliques and Bridges
    ======================================================================
    """)
    print("Size of biggest cliques:")
    print(n_biggest)
    print("Biggest cliques:")
    for x in all_cliques:
        if len(x) == n_biggest:
            print(x)
    # homophily:
    results_gender, results_bending, results_origin = analyze_homophily(data, character_data, "x_mentions_y")
    print("Homophily Gender:")
    print(results_gender)
    print("Homophily bending:")
    print(results_bending)
    print("Homophily Origin:")
    print(results_origin)
    # bridges:
    weak_articulation, strong_articulation, weak_bridges = analyze_bridges(data, reciprocal=True)
    print("Weak articulation points:")
    print(sorted(weak_articulation))
    print("Strong articulation points:")
    print(sorted(strong_articulation))
    print("Weak briges:")
    print(weak_bridges)

def visualize_sentiment():
    data = get_x_speaks_to_y_sentiment()
    datapoints = plot_sentiment_by_episode(data, "aang", "katara")
    print(datapoints)

def partition_graph():
    data = get_x_mentions_y()
    communities, labels, ari_nmi_results, coefficients_largest_communities = analyse_partitioning(data)
    print("Adjusted Rand Index and Normalized Mutual Information between partitioning algorithms")
    print(ari_nmi_results)
    print("clustering coefficients of largest community per partition algorithm")
    print(coefficients_largest_communities)
    graph = build_undirected_weighted(data)
    os.makedirs("results/partitioning", exist_ok=True)
    for alg_name, label in labels.items():
        fig, _ = visualize_partition(graph, labels=label, min_comm_size=4, show_labels=True)
        fig.savefig(f"results/partitioning/graph_{alg_name}_tuned.png")
    for alg_name, community in communities.items():
        fig, ax = plot_community_size_hist(community)
        fig.savefig(f"results/partitioning/{alg_name}_tuned")


def analyze_ego_networks():
    egos = [
        "aang",
        "zuko",
        "katara",
        "sokka",
    ]
    for ego in egos:
        min_weight = 10
        analyze_character_ego_network_per_book(ego, degree=1.0)
        analyze_character_ego_network_per_book(ego, degree=1.5)
        visualize_character_ego_networks_per_book(ego, min_weight=min_weight, degree=1.0, save=True)
        visualize_character_ego_networks_per_book(ego, min_weight=min_weight, degree=1.5, save=True)


def analyze_hits_per_book():
    """Run HITS analysis per book and save results."""
    results_dir = "results/hits"
    os.makedirs(results_dir, exist_ok=True)

    # Analyze full dataset
    data_all = get_x_mentions_y()
    G = build_graph(data_all)
    hubs, authorities = run_hits(G)

    df = pd.DataFrame({
        "character": list(hubs.keys()),
        "hub_score": list(hubs.values()),
        "authority_score": [authorities[n] for n in hubs.keys()]
    })
    df.sort_values(by="authority_score", ascending=False, inplace=True)
    df.to_csv(os.path.join(results_dir, "hits_all_books.csv"), index=False)

    # Analyze per book
    data_per_book = get_x_mentions_y_per_book()
    for book_num, data_book in enumerate(data_per_book, start=1):
        G = build_graph(data_book)
        hubs, authorities = run_hits(G)

        df = pd.DataFrame({
            "character": list(hubs.keys()),
            "hub_score": list(hubs.values()),
            "authority_score": [authorities[n] for n in hubs.keys()]
        })
        df.sort_values(by="authority_score", ascending=False, inplace=True)
        df.to_csv(os.path.join(results_dir, f"hits_book_{book_num}.csv"), index=False)

    print("HITS analysis completed for all books")


def analyze_pagerank_per_book():
    """Run PageRank analysis per book and save results."""
    results_dir = "results/pagerank"
    os.makedirs(results_dir, exist_ok=True)

    # Analyze full dataset
    data_all = get_x_mentions_y()
    G = build_graph(data_all)
    pr_scores = run_pagerank(G)

    df = pd.DataFrame({
        "character": list(pr_scores.keys()),
        "pagerank_score": list(pr_scores.values())
    })
    df.sort_values(by="pagerank_score", ascending=False, inplace=True)
    df.to_csv(os.path.join(results_dir, "pagerank_all_books.csv"), index=False)

    # Analyze per book
    data_per_book = get_x_mentions_y_per_book()
    for book_num, data_book in enumerate(data_per_book, start=1):
        G = build_graph(data_book)
        pr_scores = run_pagerank(G)

        df = pd.DataFrame({
            "character": list(pr_scores.keys()),
            "pagerank_score": list(pr_scores.values())
        })
        df.sort_values(by="pagerank_score", ascending=False, inplace=True)
        df.to_csv(os.path.join(results_dir, f"pagerank_book_{book_num}.csv"), index=False)

    print("PageRank analysis completed for all books")


def main():
    compute_network_statistics()
    partition_graph()
    run_cliques_homophily_bridges_analysis()
    # visualize_graphs()
    analyze_hits_per_book()
    analyze_pagerank_per_book()
    analyze_ego_networks()
    analyze_clustering_full_script()
    analyze_clustering_per_book()
    analyze_clustering_per_episode()
    analyze_full_script_centralities()
    analyze_each_book_centralities()
    analyze_each_episode_centralities()

    return

if __name__ == "__main__":
    main()
