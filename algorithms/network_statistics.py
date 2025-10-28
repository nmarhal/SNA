from collections import Counter, defaultdict

import networkx as nx
import pandas as pd

from model.entities.centrality_scores import CentralityScores

def build_graph(data: pd.DataFrame, use_weights: bool = False) -> nx.DiGraph:
    """
    Build a graph from a DataFrame with columns ["x", "y"] or ["x", "y", "weight"].
    If use_weights=True, weights are added to edges.
    """
    G = nx.DiGraph()

    if use_weights and "weight" in data.columns:
        for _, row in data.iterrows():
            G.add_edge(row["x"], row["y"], weight=row["weight"])
    else:
        edges = list(zip(data["x"], data["y"]))
        G.add_edges_from(edges)
    return G

class NetworkStatisticsAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data_frame = data
        self.graph = build_graph(data, use_weights=True)

    def get_number_of_vertices(self) -> int:
        return self.graph.number_of_nodes()

    def get_number_of_edges(self) -> int:
        return self.graph.number_of_edges()

    def get_in_degree_distribution(self) -> dict[int, float]:
        """
        A list that contains fractions of nodes with in-degree N
        """
        in_degree_for_each_node = [self.graph.in_degree(node) for node in self.graph.nodes()]
        counts = Counter(in_degree_for_each_node)
        return self._get_degree_distribution(counts)

    def get_out_degree_distribution(self) -> dict[int, float]:
        """
        A list that contains fractions of nodes with out-degree N
        """
        out_degree_for_each_node = [self.graph.out_degree(node) for node in self.graph.nodes()]
        counts = Counter(out_degree_for_each_node)
        return self._get_degree_distribution(counts)

    def get_weakly_connected_components_size_counts(self) -> dict[int, int]:
        components = self.get_weakly_connected_components()
        size_counts = Counter([len(component) for component in components])
        return dict(size_counts)

    def get_strongly_connected_components_size_counts(self) -> dict[int, int]:
        components = self.get_strongly_connected_components()
        size_counts = Counter([len(component) for component in components])
        return dict(size_counts)

    def get_centrality_scores(self) -> CentralityScores:
        try:
            in_degree = nx.in_degree_centrality(self.graph)
        except Exception:
            in_degree = {}
        
        try:
            out_degree = nx.out_degree_centrality(self.graph)
        except Exception:
            out_degree = {}
        
        try:
            eigenvector = nx.eigenvector_centrality(self.graph)
        except Exception:
            eigenvector = {}
        
        try:
            closeness = nx.closeness_centrality(self.graph)
        except Exception:
            closeness = {}
        
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except Exception:
            betweenness = {}
        
        return CentralityScores(
            in_degree=in_degree,
            out_degree=out_degree,
            eigenvector=eigenvector,
            closeness=closeness,
            betweenness=betweenness,
        )

    def get_clustering_coefficient(self):
        return nx.clustering(self.graph)

    def get_average_clustering(self):
        return nx.average_clustering(self.graph)

    def get_transitivity(self):
        return nx.transitivity(self.graph)

    def get_diameters_of_strongly_connected_components(self):
        strongly_connected_components = nx.strongly_connected_components(self.graph)
        component_to_diameter = {}
        for component in strongly_connected_components:
            if len(component) > 1:
                connected_subgraph = nx.subgraph(self.graph, component)
                diameter = nx.diameter(connected_subgraph)
                component_to_diameter[connected_subgraph] = diameter
        return component_to_diameter

    def get_density(self):
        return nx.density(self.graph)

    def get_weakly_connected_components(self):
        return list(nx.weakly_connected_components(self.graph))

    def get_weakly_connected_components_count(self):
        return nx.number_weakly_connected_components(self.graph)

    def get_strongly_connected_components(self):
        return list(nx.strongly_connected_components(self.graph))

    def get_strongly_connected_components_count(self):
        return nx.number_strongly_connected_components(self.graph)

    def _get_degree_distribution(self, counts: Counter[int]) -> dict[int, float]:
        nodes_count = self.get_number_of_vertices()
        distribution = dict()
        for degree in counts.keys():
            distribution[degree] = float(counts[degree]) / nodes_count
        return distribution
