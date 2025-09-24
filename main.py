from view.visualize_graphs import *
from model.read_data import *

def main():
    characters = get_characters()

    data = get_x_mentions_y()
    visualize_all_layouts(data, characters, color_by="origin")

    data = get_x_speaks_to_y()
    visualize_all_layouts(data, characters, color_by="origin")


if __name__ == "__main__":
    main()