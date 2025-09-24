import pandas as pd

import model.computeMetrics as computeMetrics
import model.readData as readData
import view.visualizeGraph as visualizeGraph

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def print_house_counts(
    df: pd.DataFrame,
    source_col: str = "Source",
    house_col: str = "Household",
    unknown_label: str = "Unknown",
    show_total: bool = True,
) -> pd.Series:
    """
    Prints and returns counts of unique characters per house,
    including a bucket for missing house values, plus a total.
    """
    pairs = df[[source_col, house_col]].drop_duplicates()  # one (Source, House) per row

    counts = (
        pairs.groupby(house_col, dropna=False)[source_col]
        .nunique()
        .sort_values(ascending=False)
    )

    # Pretty label for NaN group (display only)
    counts_display = counts.copy()
    counts_display.index = counts_display.index.map(lambda x: unknown_label if pd.isna(x) else x)

    print(counts_display.to_string())

    if show_total:
        total_unique = pairs[source_col].nunique()  # robust total of unique characters
        print(f"\nTotal unique {source_col}s: {total_unique}")

    return counts



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    book_edges = readData.get_book_1()
    characters = readData.get_characters_1()
    data = book_edges.merge(characters, how='left', on='Source')
    print_house_counts(data)
    # df_annotated = data.merge(meta, on="Source", how="left")
    # df_annotated.to_csv("Dataset/annotated_book1.csv", index=False)
    visualizeGraph.visualize_all_layouts(data)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
