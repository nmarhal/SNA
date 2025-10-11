import random
import pandas as pd
import networkx as nx
from networkx.algorithms import clique, assortativity
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
    # calculate weak articulation points
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