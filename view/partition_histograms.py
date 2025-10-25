from collections import Counter
import math
import matplotlib.pyplot as plt

def plot_community_size_hist(communities, *, ax=None, show_values=True, max_xticks=12):
    """
    Plot a clean histogram (bar chart) of community sizes.
    Only sizes that actually occur are drawn, and x-ticks are thinned automatically.

    Parameters
    ----------
    communities : list[set]
    ax : matplotlib.axes.Axes | None
    show_values : bool
        Annotate bars with counts.
    max_xticks : int
        Maximum number of x-axis tick labels to display (auto-thinned if exceeded).

    Returns
    -------
    fig, ax
    """
    sizes = [len(c) for c in communities if len(c) > 0]
    if not sizes:
        raise ValueError("No communities (or only empty ones) provided.")

    counts = Counter(sizes)
    xs = sorted(counts.keys())
    ys = [counts[x] for x in xs]

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    ax.bar(xs, ys, width=0.9, align='center')
    ax.set_xlabel("Community size (# nodes)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of community sizes")

    # Thin x-ticks if there are too many distinct sizes
    if len(xs) <= max_xticks:
        ax.set_xticks(xs)
    else:
        step = math.ceil(len(xs) / max_xticks)
        ax.set_xticks(xs[::step])

    # Optional value labels
    if show_values:
        for x, y in zip(xs, ys):
            ax.text(x, y, str(int(y)), ha="center", va="bottom", fontsize=9)
    return fig, ax