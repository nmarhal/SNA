import math
from collections import defaultdict, Counter

import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from model.entities.label_data import LabelData

def visualize_all_layouts(
    df: pd.DataFrame,
    characters: pd.DataFrame,
    label_data: LabelData | None = None,
    color_by: str | None = None,           # 'origin' | 'bending' | 'gender' | None
    *,
    seed: int = 42,
    node_size: int = 30,
    edge_width: float = 1.5,
    # data cleaning / filtering
    min_weight: int | None = None,         # keep edges with weight >= min_weight (if column exists)
    min_degree: int = 0,                   # drop nodes with degree < min_degree
    focus_gcc: bool = False,               # keep only giant (weakly) connected component
    directed: bool = False,                # visualize as DiGraph if True
    use_weight_in_layout: bool = True,     # use 'weight' for spring layout distances
    # labels
    show_labels: bool = False,
    label_top_k: int | None = None,        # label top-k by degree (None = label all when show_labels=True)
    label_nodes: list[str] | None = None,  # or specify exact nodes
    label_offset: tuple[float, float] = (0.0, 0.0),
    label_fontsize: int = 8,
    label_color: str = "black",
    label_bg: bool = True,
):
    UNKNOWN = "grey"

    # --------- color maps (hard-coded) ----------
    ORIGIN_COLORS  = {
        "earth kingdom": "green",
        "fire nation":   "red",
        "water tribe":   "blue",
        "air nomads":    "orange",
        "spirit world":  "purple",
    }
    BENDING_COLORS = {"earth":"green","fire":"red","water":"blue","air":"orange"}
    GENDER_COLORS  = {"male":"blue","female":"pink"}

    def norm_origin(x):
        if pd.isna(x) or str(x).strip()=="":
            return None
        s = str(x).strip().casefold()
        if "earth kingdom" in s: return "earth kingdom"
        if "fire nation"   in s: return "fire nation"
        if "water tribe"   in s: return "water tribe"
        if "air nomad"     in s: return "air nomads"
        if "spirit world"  in s or "spirit realm" in s: return "spirit world"
        return s  # fallback (will show as grey)

    def norm_bending(x):
        if pd.isna(x) or str(x).strip()=="":
            return None
        return str(x).strip().casefold()

    def norm_gender(x):
        if pd.isna(x) or str(x).strip()=="":
            return None
        return str(x).strip().casefold()

    def color_lookup(val):
        if color_by is None:
            return UNKNOWN
        if color_by == "origin":  return ORIGIN_COLORS.get(norm_origin(val), UNKNOWN)
        if color_by == "bending": return BENDING_COLORS.get(norm_bending(val), UNKNOWN)
        if color_by == "gender":  return GENDER_COLORS.get(norm_gender(val), UNKNOWN)
        return UNKNOWN

    # --------- prep dataframe ----------
    d = df.copy()
    d = d.dropna(subset=["x","y"])
    d = d[d["x"] != d["y"]]
    if min_weight is not None and "weight" in d.columns:
        d = d[d["weight"] >= min_weight]

    # --------- build graph ----------
    create = nx.DiGraph() if directed else nx.Graph()
    edge_attr = ["weight"] if "weight" in d.columns else None
    G = nx.from_pandas_edgelist(d, "x", "y", edge_attr=edge_attr, create_using=create)
    G.remove_edges_from(nx.selfloop_edges(G))

    # prune by degree (single pass is usually enough for decluttering)
    if min_degree > 0:
        keep = [n for n, deg in G.degree() if deg >= min_degree]
        G = G.subgraph(keep).copy()

    # focus on largest component
    if focus_gcc and G.number_of_nodes() > 0:
        comps = (nx.weakly_connected_components(G) if directed else nx.connected_components(G))
        gcc = max(comps, key=len)
        G = G.subgraph(gcc).copy()

    # --------- join node attributes for colors ----------
    if color_by:
        if "name" not in characters.columns:
            raise ValueError("`characters` must have a 'name' column.")
        if color_by not in characters.columns:
            raise ValueError(f"`characters` is missing the '{color_by}' column.")
        chars = characters.copy()
        chars["name_key"] = chars["name"].astype(str).str.strip()
        name_to_attr = dict(zip(chars["name_key"], chars[color_by]))
    else:
        name_to_attr = {}

    node_colors = [color_lookup(name_to_attr.get(str(n).strip(), None)) for n in G.nodes()]

    # --------- legend (only categories that appear) ----------
    legend_handles = []
    if color_by:
        present = {}
        for n in G.nodes():
            raw = name_to_attr.get(str(n).strip(), None)
            if color_by == "origin":
                k = norm_origin(raw); label = {
                    "earth kingdom":"Earth Kingdom",
                    "fire nation":"Fire Nation",
                    "water tribe":"Water Tribe",
                    "air nomads":"Air nomads",
                    "spirit world":"Spirit World",
                    None:"NA"
                }.get(k, "NA")
                col = ORIGIN_COLORS.get(k, UNKNOWN)
            elif color_by == "bending":
                k = norm_bending(raw); label = k if k in BENDING_COLORS else "NA"
                col = BENDING_COLORS.get(k, UNKNOWN)
            else:  # gender
                k = norm_gender(raw); label = k if k in GENDER_COLORS else "NA"
                col = GENDER_COLORS.get(k, UNKNOWN)
            present[(label, col)] = True
        present[("NA", UNKNOWN)] = True
        # nice order for origin legend
        if color_by == "origin":
            order = [("Earth Kingdom","green"),("Fire Nation","red"),
                     ("Water Tribe","blue"),("Air nomads","orange"),
                     ("Spirit World","purple"),("NA",UNKNOWN)]
            keys = [k for k in order if k in present] + [k for k in present if k not in order]
        else:
            keys = list(present.keys())
        legend_handles = [Patch(facecolor=c, edgecolor="none", label=l) for (l,c) in keys]

    # --------- layouts ----------
    weight_kw = ("weight" if ("weight" in d.columns and use_weight_in_layout) else None)
    layouts = {
        # "spring":       lambda g: nx.spring_layout(g, seed=seed, weight=weight_kw),
        "kamada_kawai": nx.kamada_kawai_layout,
        # "circular":     nx.circular_layout,
        # "shell":        nx.shell_layout,
        # "spectral":     nx.spectral_layout,
        # "random":       lambda g: nx.random_layout(g, seed=seed),
    }

    # which nodes to label?
    label_set = set()
    if show_labels:
        if label_nodes:
            label_set = {str(n).strip() for n in label_nodes} & {str(n).strip() for n in G.nodes()}
        elif label_top_k is not None:
            deg = dict(G.degree())
            label_set = {n for n, _ in sorted(deg.items(), key=lambda kv: kv[1], reverse=True)[:label_top_k]}
        else:
            label_set = set(G.nodes())
    labels_dict = {}

    # if label data is provided, add metric to the label
    for n in label_set:
        base_label = str(n)
        if label_data:
            character_name_to_metric = label_data.character_name_to_metric
            formatted_metric = f"{character_name_to_metric[n]:.4f}"
            labels_dict[n] = f"{base_label}:\n{formatted_metric}"
        else:
            labels_dict[n] = base_label

    # --------- draw ---------
    n = len(layouts); cols = 3 if n >= 3 else n; rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]

    for i, (lname, layout) in enumerate(layouts.items()):
        pos = layout(G)
        ax = axes[i]
        if label_data:
            ax.set_title(label_data.label_name, fontsize=10)
        else:
            ax.set_title(lname, fontsize=10)

        if directed:
            nx.draw_networkx_edges(G, pos, ax=ax, width=edge_width, alpha=0.6,
                                   arrows=True, arrowstyle="-|>", arrowsize=10, connectionstyle="arc3,rad=0.04")
        else:
            nx.draw_networkx_edges(G, pos, ax=ax, width=edge_width, alpha=0.6)

        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_colors)
        ax.axis("off")

        if show_labels and labels_dict:
            pos_lab = {n: (pos[n][0] + label_offset[0], pos[n][1] + label_offset[1]) for n in labels_dict}
            bbox = dict(facecolor="white", alpha=0.6, edgecolor="none", pad=0.2) if label_bg else None
            nx.draw_networkx_labels(G, pos_lab, labels=labels_dict, ax=ax,
                                    font_size=label_fontsize, font_color=label_color, bbox=bbox)

    if legend_handles:
        ncols = min(len(legend_handles), 5)
        fig.legend(handles=legend_handles, loc="lower center", ncol=ncols, frameon=False, fontsize=9)
        plt.tight_layout(rect=(0, 0.08, 1, 1))
    else:
        plt.tight_layout()

    plt.show()


def community_positions(
    G: nx.Graph | nx.DiGraph,
    labels: dict,                # node -> community_id
    *,
    weight_attr: str | None = "weight",
    seed: int = 42,
    inter_scale: float = 5.0,    # spacing between communities
    intra_scale: float = 1.0,    # size of each community “blob”
):
    """
    Compute a 2-level community-aware layout.
    Returns a dict: node -> (x,y).
    """
    # 1) collect communities
    comm_nodes = defaultdict(list)
    for n in G.nodes():
        cid = labels.get(n)
        comm_nodes[cid].append(n)
    comm_ids = list(comm_nodes.keys())

    # 2) build community meta-graph (undirected, edges weighted by sum of inter-community strength)
    CG = nx.Graph()
    CG.add_nodes_from(comm_ids)
    for u, v, d in G.edges(data=True):
        cu, cv = labels.get(u), labels.get(v)
        if cu is None or cv is None or cu == cv:
            continue
        w = d.get(weight_attr, 1.0) if weight_attr else 1.0
        if CG.has_edge(cu, cv):
            CG[cu][cv]["weight"] += w
        else:
            CG.add_edge(cu, cv, weight=w)

    # 3) place communities in the plane
    # (if only 1 community, put it at origin)
    if CG.number_of_nodes() <= 1:
        posC = {cid: (0.0, 0.0) for cid in comm_ids}
    else:
        posC = nx.spring_layout(CG, weight="weight", seed=seed)
    # scale inter-community spacing
    for cid in posC:
        x, y = posC[cid]
        posC[cid] = (inter_scale * x, inter_scale * y)

    # 4) place nodes inside each community (local spring)
    pos = {}
    for cid, nodes in comm_nodes.items():
        H = G.subgraph(nodes)
        # local layout uses original edge weights (if present)
        weight_kw = "weight" if (weight_attr and any("weight" in d for *_, d in H.edges(data=True))) else None
        if H.number_of_nodes() == 1:
            local = {nodes[0]: (0.0, 0.0)}
        else:
            local = nx.spring_layout(H, weight=weight_kw, seed=seed)

        # normalize local cloud to unit radius, then scale by community size
        # (bigger communities get a slightly larger radius to reduce overlap)
        # compute current radius
        xs, ys = zip(*local.values())
        cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
        rad = max(math.hypot(x-cx, y-cy) for x, y in local.values()) or 1.0
        # radius grows sublinearly with |nodes|
        target_r = intra_scale * (0.6 + 0.15 * math.sqrt(len(nodes)))

        for n, (x, y) in local.items():
            nxr, nyr = (x - cx)/rad * target_r, (y - cy)/rad * target_r
            ox, oy = posC[cid]
            pos[n] = (ox + nxr, oy + nyr)

    return pos

def visualize_partition(
    G: nx.Graph | nx.DiGraph,
    labels: dict,                     # node -> community_id
    *,
    min_comm_size: int = 1,
    node_size: int = 60,
    edge_width: float = 1.0,
    show_labels: bool = False,
    label_fontsize: int = 8,
    cmap_name: str = "tab20",
    seed: int = 42,
    inter_scale: float = 5.0,
    intra_scale: float = 1.0,
):
    """
    Plot a community-aware layout:
      - communities placed via spring layout on the community meta-graph,
      - nodes placed via local spring within each community “blob”.
    """
    # filter to communities meeting size threshold
    counts = Counter(c for n, c in labels.items() if c is not None)
    keep = {cid for cid, cnt in counts.items() if cnt >= min_comm_size}
    nodes_to_plot = [n for n in G.nodes() if labels.get(n) in keep]
    if not nodes_to_plot:
        raise ValueError(f"No communities with size >= {min_comm_size}.")

    H = G.subgraph(nodes_to_plot).copy()

    # positions
    pos = community_positions(H, labels, seed=seed, inter_scale=inter_scale, intra_scale=intra_scale)

    # colors per community
    comm_ids = sorted(keep, key=lambda x: str(x))
    cmap = cm.get_cmap(cmap_name, max(len(comm_ids), 3))
    color_map = {c: mcolors.to_hex(cmap(i)) for i, c in enumerate(comm_ids)}
    node_colors = [color_map[labels[n]] for n in H.nodes()]

    # legend
    legend_handles = [
        Patch(facecolor=color_map[cid], edgecolor="none", label=f"Community {cid} (n={counts[cid]})")
        for cid in sorted(keep, key=lambda c: (-counts[c], str(c)))
    ]

    # draw
    fig, ax = plt.subplots(figsize=(9, 7))
    directed = isinstance(H, nx.DiGraph)
    if directed:
        nx.draw_networkx_edges(
            H, pos, ax=ax, width=edge_width, alpha=0.6,
            arrows=True, arrowstyle="-|>", arrowsize=10, connectionstyle="arc3,rad=0.04"
        )
    else:
        nx.draw_networkx_edges(H, pos, ax=ax, width=edge_width, alpha=0.6)

    nx.draw_networkx_nodes(H, pos, ax=ax, node_color=node_colors, node_size=node_size)
    ax.axis("off")
    ax.set_title(f"Community-aware layout (≥ {min_comm_size})", fontsize=11)

    if show_labels:
        nx.draw_networkx_labels(H, pos, font_size=label_fontsize)

    ncols = min(len(legend_handles), 4)
    ax.legend(handles=legend_handles, loc="lower center", ncol=ncols, frameon=False,
              fontsize=9, bbox_to_anchor=(0.5, -0.06))

    plt.tight_layout()
    plt.show()
    return fig, ax

