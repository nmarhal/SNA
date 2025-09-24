import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def visualize_all_layouts(df: pd.DataFrame,
                          characters: pd.DataFrame,
                          color_by: str | None = None,
                          seed: int = 42,
                          node_size: int = 30,
                          edge_width: float = 1.5):
    """
    df: edges with columns ['x','y'] (optionally 'weight' ignored for width)
    characters: DataFrame with columns ['name', ...] and the chosen color_by column
    color_by: one of {'origin','bending','gender'} or None
    """

    # --- Build graph (undirected for viz) ---
    G = nx.from_pandas_edgelist(df, source="x", target="y", create_using=nx.Graph())

    # --- HARD-CODED color maps (case-insensitive) ---
    UNKNOWN = "grey"

    ORIGIN_COLORS = {
        "earth kingdom": "green",
        "fire nation":   "red",
        "water tribe":   "blue",
        "air nomads":    "orange",
        "spirit world":  "purple",
    }
    BENDING_COLORS = {
        "earth": "green",
        "fire":  "red",
        "water": "blue",
        "air":   "orange",
    }
    GENDER_COLORS = {
        "male":   "blue",
        "female": "pink",
    }

    # --- Normalizers so variants map correctly (e.g., "Water Tribe (Southern)" -> "water tribe") ---
    def norm_origin(x):
        if pd.isna(x) or x is None or str(x).strip() == "":
            return None
        s = str(x).strip().casefold()
        if "earth kingdom" in s:
            return "earth kingdom"
        if "fire nation" in s:
            return "fire nation"
        if "water tribe" in s:
            return "water tribe"
        if "air nomad" in s:
            return "air nomads"
        if "spirit world" in s or "spirit realm" in s:
            return "spirit world"
        return s  # fallback (may go to UNKNOWN later)

    def norm_bending(x):
        if pd.isna(x) or x is None or str(x).strip() == "":
            return None
        return str(x).strip().casefold()

    def norm_gender(x):
        if pd.isna(x) or x is None or str(x).strip() == "":
            return None
        return str(x).strip().casefold()

    def color_lookup(raw_value):
        if color_by is None:
            return UNKNOWN
        if color_by == "origin":
            k = norm_origin(raw_value)
            return ORIGIN_COLORS.get(k, UNKNOWN)
        if color_by == "bending":
            k = norm_bending(raw_value)
            return BENDING_COLORS.get(k, UNKNOWN)
        if color_by == "gender":
            k = norm_gender(raw_value)
            return GENDER_COLORS.get(k, UNKNOWN)
        return UNKNOWN

    # --- Join character attributes to nodes ---
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

    # --- Build legend only for categories that actually appear ---
    legend_handles = []
    if color_by:
        present = {}
        for n in G.nodes():
            raw = name_to_attr.get(str(n).strip(), None)
            col = color_lookup(raw)

            if color_by == "origin":
                k = norm_origin(raw)
                label = {
                    "earth kingdom": "Earth Kingdom",
                    "fire nation":   "Fire Nation",
                    "water tribe":   "Water Tribe",
                    "air nomads":    "Air nomads",
                    "spirit world":  "Spirit World",
                    None:            "NA",
                }.get(k, "NA")
            elif color_by == "bending":
                k = norm_bending(raw)
                label = { "earth":"earth", "fire":"fire", "water":"water", "air":"air", None:"NA" }.get(k, "NA")
            else:  # gender
                k = norm_gender(raw)
                label = { "male":"male", "female":"female", None:"NA" }.get(k, "NA")

            present[(label, col)] = True

        # Always include NA/unknown in legend
        present[("NA", UNKNOWN)] = True
        legend_handles = [Patch(facecolor=c, edgecolor="none", label=l) for (l, c) in present.keys()]

    # --- Layouts & drawing (constant edge width) ---
    layouts = {
        "spring":       lambda g: nx.spring_layout(g, seed=seed),
        "kamada_kawai": nx.kamada_kawai_layout,
        "circular":     nx.circular_layout,
        "shell":        nx.shell_layout,
        "spectral":     nx.spectral_layout,
        "random":       lambda g: nx.random_layout(g, seed=seed),
    }

    n = len(layouts)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for i, (lname, layout) in enumerate(layouts.items()):
        pos = layout(G)
        ax = axes[i]
        ax.set_title(lname, fontsize=10)

        nx.draw_networkx_edges(G, pos, ax=ax, width=edge_width, alpha=0.6)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_colors)
        ax.axis("off")

    if legend_handles:
        ncols = min(len(legend_handles), 5)
        fig.legend(handles=legend_handles, loc="lower center", ncol=ncols, frameon=False, fontsize=9)
        plt.tight_layout(rect=(0, 0.08, 1, 1))
    else:
        plt.tight_layout()

    plt.show()
