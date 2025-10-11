import random
import pandas as pd
import networkx as nx
from networkx.algorithms import clique, assortativity
from networkx.algorithms.community import girvan_newman
from networkx.algorithms.community.quality import modularity
import community as community_louvain
import igraph as ig
import leidenalg as la
import os


# Base path to the data folder (relative to algorithms/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "model", "data")


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

def build_graph_with_attributes(data: pd.DataFrame, character_data: pd.DataFrame) -> nx.DiGraph:
    directed_graph = nx.DiGraph()
    directed_graph.add_weighted_edges_from(data[["x", "y", "weight"]].itertuples(index=False, name=None))

    # Attach node attributes
    character_data["bending"] = character_data["bending"].fillna("unknown")
    attr_map = character_data.set_index("name")[["gender", "bending", "origin"]].to_dict(orient="index")
    nx.set_node_attributes(directed_graph, attr_map)
    return directed_graph

def build_undirected_weighted(data: pd.DataFrame) -> nx.Graph:
    """
   Create an undirected weighted graph summing reciprocal weights.
   """
    directed_graph = nx.DiGraph()
    directed_graph.add_weighted_edges_from(data[["x", "y", "weight"]].itertuples(index=False, name=None))

    undirected_graph = nx.Graph()
    undirected_graph.add_nodes_from(directed_graph.nodes(data=True))
    for u, v, d in directed_graph.edges(data=True):
        w = d.get("weight", 1.0) if "weight" else 1.0
        if undirected_graph.has_edge(u, v):
            undirected_graph[u][v]["weight"] += w
        else:
            undirected_graph.add_edge(u, v, weight=w)
    return undirected_graph

def run_hits(graph: nx.DiGraph, max_iter: int = 1000, tol: float = 1e-8):
    """
    Run HITS algorithm on a graph.
    Returns two dicts: hubs and authorities.
    """
    hubs, authorities = nx.hits(graph, max_iter=max_iter, tol=tol, normalized=True)
    return hubs, authorities

def run_pagerank(graph: nx.DiGraph, alpha: float = 0.85, max_iter: int = 1000, tol: float = 1e-8,
                 weight: str = "weight"):
    """
    Run PageRank on a graph, using weights if available.
    Returns a dict {node: pagerank_score}.
    """
    pr = nx.pagerank(graph, alpha=alpha, max_iter=max_iter, tol=tol,
                     weight=weight if weight in graph.edges[list(graph.edges)[0]] else None)
    return pr

def run_cliques(graph: nx.Graph):
    """
    Run Cliques algorithm on a graph, does not use weights nor direction
    :param graph: The graph to run cliques on.
    :return: size of largest clique, list of all cliques
    """
    # enumerate ALL cliques
    all_cliques = list(clique.enumerate_all_cliques(graph))
    # size of the largest clique
    n_biggest = 0
    for C in clique.find_cliques(graph):
        lc = len(C)
        if lc > n_biggest:
            n_biggest = lc
    return n_biggest, all_cliques

def run_homophily(graph: nx.DiGraph, attr: str, permutations: int = 0):
    n_nodes, n_edges = graph.number_of_nodes(), graph.number_of_edges()

    # 1) Assortativity (categorical) on directed graph
    r = assortativity.attribute_assortativity_coefficient(graph, attr)

    # 2) Mixing matrices
    M = assortativity.attribute_mixing_matrix(graph, attr, normalized=False)
    M_norm = assortativity.attribute_mixing_matrix(graph, attr, normalized=True)

    # 3) Edgewise homophily & E–I index
    same = 0.0
    total = 0.0
    for u, v, d in graph.edges(data=True):
        w = 1.0
        total += w
        if graph.nodes[u][attr] == graph.nodes[v][attr]:
            same += w
    edgewise_hom = same / total if total > 0 else float("nan")
    E_minus_I = ((total - same) - same) / total if total > 0 else float("nan")

    # 4) Optional permutation test
    p_value = None
    if permutations and permutations > 0:
        rng = random.Random(1)
        orig_vals = {n: graph.nodes[n][attr] for n in graph.nodes()}
        vals = list(orig_vals.values())
        null_stats = []
        for _ in range(permutations):
            rng.shuffle(vals)
            for n, v in zip(graph.nodes(), vals):
                graph.nodes[n][attr] = v
            rr = assortativity.attribute_assortativity_coefficient(graph, attr)
            null_stats.append(rr)
        # restore
        for n, v in orig_vals.items():
            graph.nodes[n][attr] = v
        ge = sum(1 for z in null_stats if abs(z) >= abs(r))
        p_value = (ge + 1) / (permutations + 1)

    return {
        "assortativity": r,
        "assortativity_p_value": p_value,
        "edgewise_homophily": edgewise_hom,
        "E_minus_I_index": E_minus_I,
        "mixing_matrix": M.tolist(),
        "mixing_matrix_norm": M_norm.tolist(),
    }

def run_bridges(graph: nx.DiGraph, graph_und: nx.Graph):
    """
    Compute three bridge-like structures in a directed network.

    Returns
    weak_articulation : list
        Nodes whose removal increases the number of connected components when direction is ignored.
    strong_articulation : list
        Nodes whose removal increases the number of strongly connected components in the directed graph.
    weak_bridges : list[tuple]
        Edges (u, v) that are bridges in the undirected sense: removing the edge increases the number of connected components.
    """
    weak_articulation = list(nx.articulation_points(graph_und))
    scc = nx.number_strongly_connected_components(graph)
    strong_articulation = []
    for v in graph.nodes():
        new_graph = graph.copy()
        new_graph.remove_node(v)
        if nx.number_strongly_connected_components(new_graph) > scc:
            strong_articulation.append(v)
    weak_bridges = list(nx.bridges(graph_und))
    return weak_articulation, strong_articulation, weak_bridges

def run_partition_girvan(graph: nx.Graph, k: int | None = None):
    """
        Girvan–Newman partition algorithm.
        DG : nx.DiGraph
            directed graph with weights
        k : int | None
            If set, return the partition after k splits.
            If None, returns the partition with the highest modularity encountered during the sequence.

        communities : list[set]
            List of node sets (one set per community).
        labels : dict
            Mapping node -> community_id
        """
    comp_gen = girvan_newman(graph)
    best = None
    best_Q = float("-inf")
    if k is not None:
        # advance generator to the k-th split (k+1 communities)
        for i, part in enumerate(comp_gen):
            if i == k:
                communities = [set(c) for c in part]
                labels = {n: idx for idx, c in enumerate(communities) for n in c}
                return communities, labels
        # if ended early, fall back to last
        communities = [set(c) for c in part]
        labels = {n: idx for idx, c in enumerate(communities) for n in c}
        return communities, labels
    else:
        # scan and pick max modularity level
        for part in comp_gen:
            communities = [set(c) for c in part]
            Q = modularity(graph, communities, weight="weight")
            if Q > best_Q:
                best_Q = Q
                best = communities
            if len(communities) >= graph.number_of_nodes():
                break
        communities = best if best is not None else [set(graph.nodes())]
        labels = {n: idx for idx, c in enumerate(communities) for n in c}
        return communities, labels

def run_partition_louvain(graph: nx.Graph, resolution: float = 1.0, random_state: int | None = None,):
    """
    Louvain modularity optimization (requires `python-louvain` package).

    Returns
    -------
    communities : list[set], labels : dict
    """
    part = community_louvain.best_partition(graph, weight="weight",resolution=resolution, random_state=random_state)
    # build list[set] from labels
    comm_map = {}
    for n, cid in part.items():
        comm_map.setdefault(cid, set()).add(n)
    # reindex communities 0..C-1
    remap = {old: i for i, old in enumerate(sorted(comm_map))}
    labels = {n: remap[cid] for n, cid in part.items()}
    # reorder communities
    communities = [set() for _ in range(len(remap))]
    for n, cid in labels.items():
        communities[cid].add(n)
    return communities, labels

def run_partition_leiden(graph: nx.Graph, resolution: float = 1.0, n_iterations: int = -1, random_state: int | None = None,):
    """
        Leiden community detection (requires `igraph` and `leidenalg`).

        Notes
        -----
        - Converts to an undirected igraph with summed weights for reciprocity.
        - Uses RBConfigurationVertexPartition (Leiden with resolution parameter).
        - Set `n_iterations=-1` to let the algorithm run until convergence.

        Returns
        -------
        communities : list[set], labels : dict
        """
    # Build igraph
    node_index = {n: i for i, n in enumerate(graph.nodes())}
    edges = [(node_index[u], node_index[v]) for u, v in graph.edges()]
    weights = [graph[u][v].get("weight", 1.0) for u, v in graph.edges()]
    ig_graph = ig.Graph(edges=edges, directed=False)
    ig_graph.add_vertices(len(graph) - ig_graph.vcount())  # ensure all vertices exist
    ig_graph.vs["name"] = list(graph.nodes())
    ig_graph.es["weight"] = weights

    rng = la.RNG(random_state) if random_state is not None else None
    part = la.find_partition(
        ig_graph,
        la.RBConfigurationVertexPartition,
        weights="weight",
        resolution_parameter=resolution,
        n_iterations=n_iterations,
        seed=rng,
    )
    # Convert back
    communities = [set(ig_graph.vs[idx]["name"] for idx in comm) for comm in part]
    labels = {}
    for cid, comm in enumerate(communities):
        for n in comm:
            labels[n] = cid
    return communities, labels

def save_hits_results(hubs: dict, authorities: dict, filename: str):
    """
    Save HITS hubs and authorities to CSV.
    """
    df = pd.DataFrame({
        "character": list(hubs.keys()),
        "hub_score": list(hubs.values()),
        "authority_score": [authorities[n] for n in hubs.keys()]
    })
    df.sort_values(by="authority_score", ascending=False, inplace=True)
    df.to_csv(os.path.join(DATA_DIR, filename), index=False)


def save_pagerank_results(scores: dict, filename: str):
    """
    Save PageRank scores to CSV.
    """
    df = pd.DataFrame({
        "character": list(scores.keys()),
        "pagerank_score": list(scores.values())
    })
    df.sort_values(by="pagerank_score", ascending=False, inplace=True)
    df.to_csv(os.path.join(DATA_DIR, filename), index=False)

def analyze_hits(data: pd.DataFrame, name: str):
    """
    Build graph and run HITS, saving results to CSV.
    """
    G = build_graph(data)
    hubs, authorities = run_hits(G)
    save_hits_results(hubs, authorities, f"hits_{name}.csv")
    return hubs, authorities


def analyze_pagerank(data: pd.DataFrame, name: str, alpha: float = 0.85,
                     use_weights: bool = True):
    """
    Build graph and run PageRank, saving results to CSV.
    """
    G = build_graph(data, use_weights=use_weights)
    pr_scores = run_pagerank(G, alpha=alpha)
    save_pagerank_results(pr_scores, f"pagerank_{name}.csv")
    return pr_scores

def analyze_cliques(data: pd.DataFrame, name: str, reciprocal: bool = True):
    graph = build_graph(data, use_weights=False)
    graph = graph.to_undirected(reciprocal=reciprocal) # remove directions from graph, keeps only bidirectional edges
    n_biggest, all_cliques = run_cliques(graph)
    return n_biggest, all_cliques

def analyze_homophily(data: pd.DataFrame, character_data: pd.DataFrame, name: str):
    graph = build_graph_with_attributes(data, character_data)
    results_gender = run_homophily(graph=graph, attr="gender", permutations = 100)
    results_bending = run_homophily(graph=graph, attr="bending", permutations = 100)
    results_origin = run_homophily(graph=graph, attr="origin", permutations = 100)
    return results_gender, results_bending, results_origin

def analyze_bridges(data: pd.DataFrame, reciprocal: bool = True):
    graph = build_graph(data)
    graph_und = graph.to_undirected(reciprocal=reciprocal)  # remove directions from graph, keeps only bidirectional edges
    return run_bridges(graph, graph_und)

def analyse_partitioning(data: pd.DataFrame):
    graph = build_undirected_weighted(data)
    g_communities, g_labels = run_partition_girvan(graph)
    l_communities, l_labels = run_partition_louvain(graph)
    le_communities, le_labels = run_partition_louvain(graph)
    return g_communities, g_labels, l_communities, l_labels, le_communities, le_labels
