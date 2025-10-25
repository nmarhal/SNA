import csv
import os

tables_dir = "visualizations/tables"

def save_clustering_coefficient_to_csv(
    clustering_coefficient: dict,
    average_clustering: float,
    transitivity: float,
    heading: str
):
    clustering_tables_dir = os.path.join(tables_dir, "clustering")
    os.makedirs(clustering_tables_dir, exist_ok=True)

    sorted_data = sorted(clustering_coefficient.items(), key=lambda x: x[1], reverse=True)

    filename = heading.replace(":", "").replace(" ", "_").replace("/", "_") + ".csv"
    filepath = os.path.join(clustering_tables_dir, filename)

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'coefficient'])
        writer.writerow(['average clustering coefficient', average_clustering])
        writer.writerow(['transitivity', transitivity])
        for character, coefficient in sorted_data:
            writer.writerow([character, coefficient])

    print(f"Saved clustering coefficient table to {filepath}")
