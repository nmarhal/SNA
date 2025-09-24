from view.visualize_graphs import *
from model.read_data import *

def main():
    characters = get_characters()

    min_weight = 20
    min_degree = 2
    color_by = "origin"
    show_labels = True
    label_top_k = 10
    directed = True

    data = get_x_mentions_y()
    visualize_all_layouts(data,
                          characters,
                          color_by=color_by,
                          min_weight=min_weight,
                          min_degree=min_degree,
                          show_labels=show_labels,
                          label_top_k=label_top_k,
                          directed=directed)

    data = get_x_speaks_to_y()
    visualize_all_layouts(data,
                          characters,
                          color_by=color_by,
                          min_weight=min_weight,
                          min_degree=min_degree,
                          show_labels=show_labels,
                          label_top_k=label_top_k,
                          directed=directed)


if __name__ == "__main__":
    main()