import csv
import os

tables_dir = "visualizations/tables"

def _fix_heading_characters(heading):
    return heading.replace(":", "").replace(" ", "_").replace("/", "_") + ".csv"

def save_clustering_coefficient_to_csv(
    clustering_coefficient: dict,
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
        for character, coefficient in sorted_data:
            writer.writerow([character, f"{coefficient:.3f}"])

def save_centrality_to_csv(
    centrality_dict: dict,
    centrality_name: str,
    heading: str
):
    centrality_dir = os.path.join(f"{tables_dir}/centralities", centrality_name)
    os.makedirs(centrality_dir, exist_ok=True)
    
    sorted_data = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
    
    filename = _fix_heading_characters(heading)
    filepath = os.path.join(centrality_dir, filename)
    
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", centrality_name])
        for character, score in sorted_data:
            writer.writerow([character, f"{score:.3f}"])