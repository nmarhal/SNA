import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def visualize_all_layouts(
    df: pd.DataFrame,
    characters: pd.DataFrame,
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
        "spring":       lambda g: nx.spring_layout(g, seed=seed, weight=weight_kw),
        "kamada_kawai": nx.kamada_kawai_layout,
        "circular":     nx.circular_layout,
        "shell":        nx.shell_layout,
        "spectral":     nx.spectral_layout,
        "random":       lambda g: nx.random_layout(g, seed=seed),
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
    labels_dict = {n: str(n) for n in label_set}

    # --------- draw ---------
    n = len(layouts); cols = 3; rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for i, (lname, layout) in enumerate(layouts.items()):
        pos = layout(G)
        ax = axes[i]; ax.set_title(lname, fontsize=10)

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
