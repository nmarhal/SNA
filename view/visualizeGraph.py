import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
def _node_attr_map(df, source_attr_col="House", target_attr_col=None):
    """Build node -> attribute map from Source (and optionally Target) metadata."""
    node_to_attr = {}
    if source_attr_col:
        node_to_attr.update(
            df[["Source", source_attr_col]]
            .dropna()
            .drop_duplicates("Source")
            .set_index("Source")[source_attr_col]
            .to_dict()
        )
    if target_attr_col:
        tgt_map = (
            df[["Target", target_attr_col]]
            .dropna()
            .drop_duplicates("Target")
            .set_index("Target")[target_attr_col]
            .to_dict()
        )
        # keep Source value if present; otherwise use Target's
        for k, v in tgt_map.items():
            node_to_attr.setdefault(k, v)
    return node_to_attr

def _categorical_cmap(values, cmap_name="tab20"):
    """Return a dict value -> RGBA using a matplotlib colormap."""
    # unique values in order of first appearance, NaNs dropped
    uniques = pd.unique(pd.Series(list(values)).dropna())
    N = len(uniques)
    # For many categories, a continuous map (e.g. 'turbo' or 'viridis') separates better than tab20
    base = cmap_name if N <= 20 else "turbo"
    cmap = mpl.cm.get_cmap(base, N)  # discretize into N distinct colors
    return {val: cmap(i) for i, val in enumerate(uniques)}

def visualize_all_layouts(
    df: pd.DataFrame,
    color_by: str = "Household",                 # label only
    source_attr_col: str | None = None,      # defaults to color_by
    target_attr_col: str | None = None,      # pass if you merged Target metadata too
    cmap_name: str = "tab20",
    unknown_color = (0.6, 0.6, 0.6, 1.0),
    legend: bool = True,
    legend_max: int = 14,
    seed: int = 42,
    node_size: int = 10
):
    source_attr_col = source_attr_col or color_by

    # Build graph
    G = nx.from_pandas_edgelist(df, source="Source", target="Target", create_using=nx.Graph())

    # Node -> attribute (e.g., House)
    node_to_attr = _node_attr_map(df, source_attr_col, target_attr_col)

    # Value -> color (unique per house present)
    value_to_color = _categorical_cmap(node_to_attr.values(), cmap_name=cmap_name)

    # Colors in graph node order
    node_colors = [value_to_color.get(node_to_attr.get(n), unknown_color) for n in G.nodes()]

    # Layouts
    layouts = {
        "spring": lambda g: nx.spring_layout(g, seed=seed),
        "kamada_kawai": nx.kamada_kawai_layout,
        "circular": nx.circular_layout,
        "shell": nx.shell_layout,
        "spectral": nx.spectral_layout,
        "random": lambda g: nx.random_layout(g, seed=seed),
    }

    # Subplots
    n = len(layouts)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for i, (name, layout) in enumerate(layouts.items()):
        pos = layout(G)
        ax = axes[i]
        ax.set_title(name, fontsize=10)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_colors)
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.7)
        ax.axis("off")

    # Hide unused subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    # (Optional) legend with up to legend_max entries
    if legend and value_to_color:
        shown = list(value_to_color.items())[:legend_max]
        handles = [
            mpl.lines.Line2D([0],[0], marker='o', linestyle='', markersize=6, color=c, label=str(v))
            for v, c in shown
        ]
        leg = fig.legend(handles=handles, title=f"{color_by}", loc="lower center", ncol=min(6, len(shown)))
        leg._legend_box.align = "left"

    plt.tight_layout(rect=(0, 0.05, 1, 1))  # leave space for legend at bottom
    plt.show()