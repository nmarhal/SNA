import pandas as pd
import networkx as nx
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
