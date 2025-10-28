from collections import Counter
import math
import matplotlib.pyplot as plt


def plot_degree_distribution(degree_proportions, *, ax=None, show_values=True, max_xticks=20, title="Degree Distribution", xlabel="Degree"):
    if not degree_proportions:
        raise ValueError("Empty degree distribution provided.")

    degrees = sorted(degree_proportions.keys())
    proportions = [degree_proportions[d] for d in degrees]

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    ax.bar(degrees, proportions, width=0.9, align='center')
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Proportion of nodes")
    ax.set_title(title)

    if len(degrees) <= max_xticks:
        ax.set_xticks(degrees)
    else:
        step = math.ceil(len(degrees) / max_xticks)
        ax.set_xticks(degrees[::step])

    if show_values:
        for d, p in zip(degrees, proportions):
            ax.text(d, p, f"{p:.2f}", ha="center", va="bottom", fontsize=6)

    return fig, ax


def plot_in_out_degree_distribution(in_degree_proportions, out_degree_proportions, *, show_values=True, max_xticks=20, figsize=(12, 5)):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    plot_degree_distribution(
        in_degree_proportions,
        ax=ax1,
        show_values=show_values,
        max_xticks=max_xticks,
        title="In-Degree Distribution",
        xlabel="In-Degree"
    )
    plot_degree_distribution(
        out_degree_proportions,
        ax=ax2,
        show_values=show_values,
        max_xticks=max_xticks,
        title="Out-Degree Distribution",
        xlabel="Out-Degree"
    )

    plt.tight_layout()
    return fig, (ax1, ax2)

