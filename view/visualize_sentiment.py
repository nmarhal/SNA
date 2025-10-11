import pandas as pd
import matplotlib.pyplot as plt
from typing import Sequence, Union, Optional, Iterable

def plot_sentiment_by_episode(
    df: pd.DataFrame,
    speaker: Union[str, Sequence[str]],
    target: Union[str, Sequence[str]],
    score_col: str = "compound",
):
    """
    Plot episode-by-episode sentiment of speaker(s) towards target(s).

    Args:
        df: pandas DataFrame with columns ['x', 'y', 'episode', score_col].
        speaker: Name or list/sequence of speaker names (case-insensitive).
        target: Name or list/sequence of target names (case-insensitive).
        score_col: Column holding the sentiment score (default 'compound' in [-1, 1]).

    Returns:
        agg: DataFrame with columns ['episode', score_col] (mean sentiment per episode)
             for all rows where x in speakers and y in targets.
    """

    def _to_lower_set(val: Union[str, Iterable[str]]) -> set:
        # Accept a single string or any iterable of strings; return a lowercase set
        if isinstance(val, str):
            return {val.strip().lower()}
        try:
            return {str(v).strip().lower() for v in val}
        except TypeError:
            # Non-iterable fallback
            return {str(val).strip().lower()}

    speakers = _to_lower_set(speaker)
    targets = _to_lower_set(target)

    # Prepare lowercase comparison columns (robust to non-strings / NaNs)
    x_lower = df["x"].astype(str).str.lower()
    y_lower = df["y"].astype(str).str.lower()

    # Filter rows where speaker and target match any in the provided sets
    mask = x_lower.isin(speakers) & y_lower.isin(targets)

    sub = df.loc[mask, ["episode", score_col]].copy()
    sub = sub.dropna(subset=["episode", score_col])

    if sub.empty:
        # Nothing to plot; return empty result gracefully
        print("No matching rows for the given speaker(s) and target(s).")
        return pd.DataFrame(columns=["episode", score_col])

    # Aggregate by episode (mean sentiment)
    agg = (
        sub.groupby("episode", as_index=False)[score_col]
        .mean()
        .sort_values("episode")
    )

    # Plot
    plt.figure()
    plt.plot(agg["episode"], agg[score_col], marker="o")
    plt.axhline(0.0, linestyle="--")
    plt.ylim(-1, 1)
    plt.xlabel("Episode")
    plt.ylabel(f"Sentiment (mean {score_col})")

    speakers_title = ", ".join(sorted(speakers))
    targets_title = ", ".join(sorted(targets))
    plt.title(f"Sentiment by Episode: {speakers_title} → {targets_title}")
    plt.grid(True, linestyle=":", linewidth=0.5)
    plt.show()

    return agg