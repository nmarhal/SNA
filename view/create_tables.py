import csv
import os

tables_dir = "visualizations/tables"

def _fix_heading_characters(heading):
    return heading.replace(":", "").replace(" ", "_").replace("/", "_") + ".csv"

def save_clustering_coefficient_to_csv(
    clustering_coefficient: dict,
    average_clustering: float,
    transitivity: float,
    heading: str
):
    clustering_tables_dir = os.path.join(tables_dir, "clustering")
    os.makedirs(clustering_tables_dir, exist_ok=True)

    sorted_data = sorted(clustering_coefficient.items(), key=lambda x: x[1], reverse=True)

    filename = _fix_heading_characters(heading)
    filepath = os.path.join(clustering_tables_dir, filename)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'coefficient'])
        writer.writerow(['average clustering coefficient', average_clustering])
        writer.writerow(['transitivity', transitivity])
        for character, coefficient in sorted_data:
            writer.writerow([character, coefficient])

def save_centralities_to_csv(
    centralities: dict[str, tuple[float, float, float]],
    heading: str
):
    clustering_tables_dir = os.path.join(tables_dir, "centrality")
    os.makedirs(clustering_tables_dir, exist_ok=True)

    sorted_data = sorted(centralities.items(), key=lambda x: x[1], reverse=True)

    filename = _fix_heading_characters(heading)
    filepath = os.path.join(clustering_tables_dir, filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "in-degree", "eigenvector", "betweenness"])
        for character, (in_degree, eigenvector, betweenness) in sorted_data:
            writer.writerow([character, in_degree, eigenvector, betweenness])