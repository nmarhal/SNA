from collections import Counter

import pandas as pd
import networkx as nx
from networkx.classes import number_of_nodes
from numpy.ma.core import outer

from algorithms.graph_algorithms import build_graph
from model.entities.centrality_scores import CentralityScores


class NetworkStatisticsAnalyzer:
    """
    number of vertices - done
    number of edges - done
    degree distribution (in-degree and out degree) - done
    centrality indices - done
    clustering coefficient
    network diameter
    density
    number of connected components
    size of the connected components
    """

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

    def get_centrality_scores(self) -> CentralityScores:
        return CentralityScores(
            in_degree=nx.in_degree_centrality(self.graph),
            out_degree=nx.out_degree_centrality(self.graph),
            eigenvector=nx.eigenvector_centrality(self.graph),
            closeness=nx.closeness_centrality(self.graph),
            betweenness=nx.betweenness_centrality(self.graph),
        )

    def _get_degree_distribution(self, counts: Counter[int]) -> dict[int, float]:
        nodes_count = self.get_number_of_vertices()
        distribution = dict()
        for degree in counts.keys():
            distribution[degree] = float(counts[degree]) / nodes_count
        return distribution
