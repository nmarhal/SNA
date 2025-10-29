from matplotlib import pyplot as plt
import matplotlib.patheffects as path_effects

from algorithms.graph_algorithms import *
from model.book_names import BOOK_NAMES
from model.read_data import *


def _extract_ego_network(data: pd.DataFrame, ego_character: str, radius: int = 1, degree: float = 1.5):
    """
    Extract an egocentric network centered on a specific character.

    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame with columns ["x", "y", "weight"]
    ego_character : str
        The character to center the ego network around
    radius : int
        How many hops away from ego to include (default 1 = direct connections only)
    degree : float
        Type of ego network to extract:
        - 1.0: Only direct connections (ego ↔ others)
        - 1.5: Direct connections + connections between those others

    Returns:
    --------
    ego_data : pd.DataFrame
        Filtered DataFrame containing only edges in the ego network
    ego_graph : nx.DiGraph
        NetworkX graph of the ego network
    """
    # Build full graph using existing function
    G = build_graph(data, use_weights=True)

    # Check if ego character exists in the graph
    if ego_character not in G.nodes():
        print(f"Warning: {ego_character} not found in this book's network")
        return pd.DataFrame(columns=["x", "y", "weight"]), nx.DiGraph()

    # Extract ego network (undirected for radius calculation)
    G_undirected = G.to_undirected()
    ego_nodes = nx.ego_graph(G_undirected, ego_character, radius=radius).nodes()

    # Create subgraph maintaining directionality
    ego_graph = G.subgraph(ego_nodes).copy()

    # If degree is 1.0, filter to only edges involving the ego character
    if degree == 1.0:
        edges_to_keep = []
        for u, v, data_dict in ego_graph.edges(data=True):
            if u == ego_character or v == ego_character:
                edges_to_keep.append((u, v, data_dict))

        # Create new graph with only ego-connected edges
        ego_graph = nx.DiGraph()
        ego_graph.add_nodes_from(ego_nodes)
        for u, v, data_dict in edges_to_keep:
            ego_graph.add_edge(u, v, **data_dict)

    # Convert back to DataFrame
    ego_edges = []
    for u, v, data_dict in ego_graph.edges(data=True):
        ego_edges.append({
            "x": u,
            "y": v,
            "weight": data_dict.get("weight", 1)
        })

    ego_data = pd.DataFrame(ego_edges)

    return ego_data, ego_graph


def _analyze_ego_network_stats(ego_character: str, ego_data: pd.DataFrame, book_name: str):
    """
    Analyze and print statistics for an ego network.
    """
    if ego_data.empty:
        print(f"\n{book_name}: No network data for {ego_character}")
        return

    # Build graph using existing function
    G = build_graph(ego_data, use_weights=True)

    print(f"\n{'=' * 60}")
    print(f"{book_name}: {ego_character}'s Ego Network")
    print(f"{'=' * 60}")

    # Basic stats
    print(f"\nNetwork Size:")
    print(f"  Total nodes: {G.number_of_nodes()}")
    print(f"  Total edges: {G.number_of_edges()}")

    # Connections TO ego (who mentions Zuko)
    in_edges = [(u, d['weight']) for u, v, d in G.in_edges(ego_character, data=True)]
    in_edges_sorted = sorted(in_edges, key=lambda x: x[1], reverse=True)

    print(f"\n  Characters mentioning {ego_character} (incoming):")
    for char, weight in in_edges_sorted[:10]:  # Top 10
        print(f"    {char}: {weight}")

    # Connections FROM ego (who Zuko mentions)
    out_edges = [(v, d['weight']) for u, v, d in G.out_edges(ego_character, data=True)]
    out_edges_sorted = sorted(out_edges, key=lambda x: x[1], reverse=True)

    print(f"\n  Characters {ego_character} mentions (outgoing):")
    for char, weight in out_edges_sorted[:10]:  # Top 10
        print(f"    {char}: {weight}")

    # Reciprocal relationships
    reciprocal = []
    for v, out_weight in out_edges:
        in_weight = next((w for u, w in in_edges if u == v), 0)
        if in_weight > 0:
            reciprocal.append((v, out_weight, in_weight, out_weight + in_weight))

    reciprocal_sorted = sorted(reciprocal, key=lambda x: x[3], reverse=True)

    print(f"\n  Reciprocal relationships (total mentions):")
    for char, out_w, in_w, total in reciprocal_sorted[:10]:
        print(f"    {char}: {total} (out: {out_w}, in: {in_w})")


def analyze_character_ego_network_per_book(character_name: str, degree: float = 1.5):
    """
    Analyze any character's ego network for each book to track relationship evolution.

    Parameters:
    -----------
    character_name : str
        Name of the character to analyze (will be converted to lowercase)
    degree : float
        1.0 for 1-degree (direct only), 1.5 for 1.5-degree (direct + inter-connections)
    """
    all_books = get_x_mentions_y_per_book()
    character_lower = character_name.lower()

    degree_str = "1-DEGREE" if degree == 1.0 else "1.5-DEGREE"
    print("\n" + "=" * 70)
    print(f"{character_name.upper()}'S {degree_str} EGO NETWORK ANALYSIS ACROSS BOOKS")
    print("=" * 70)

    for book_number, book_data in enumerate(all_books, start=1):
        book_name = f"Book {book_number}: {BOOK_NAMES[book_number]}"

        # Extract ego network (radius=1 means direct connections only)
        ego_data, ego_graph = _extract_ego_network(book_data, character_lower, radius=1, degree=degree)

        # Analyze and print statistics
        _analyze_ego_network_stats(character_lower, ego_data, book_name)

    print("\n" + "=" * 70)


def _save_centrality_table(centrality: dict, ego_character: str, book_name: str, save_path: str):
    """
    Save eigenvector centrality as a table image.

    Parameters:
    -----------
    centrality : dict
        Dictionary of character names to centrality values
    ego_character : str
        Name of the ego character
    book_name : str
        Name/title for the table
    save_path : str
        Path to save the table image
    """
    if not centrality:
        print(f"No centrality data to save for {ego_character} in {book_name}")
        return

    # Sort by centrality (descending)
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    # Prepare data for table
    characters = [char.capitalize() for char, _ in sorted_centrality]
    centrality_values = [f"{cent:.4f}" for _, cent in sorted_centrality]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, max(6, len(characters) * 0.4)))
    ax.axis('tight')
    ax.axis('off')

    # Create table
    table_data = [[char, cent] for char, cent in zip(characters, centrality_values)]
    table = ax.table(cellText=table_data,
                     colLabels=['Character', 'Eigenvector Centrality'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.6, 0.4])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)

    # Header styling
    for i in range(2):
        cell = table[(0, i)]
        cell.set_facecolor('#3498DB')
        cell.set_text_props(weight='bold', color='white')

    # Highlight ego character
    for i, (char, _) in enumerate(sorted_centrality, start=1):
        if char == ego_character:
            table[(i, 0)].set_facecolor('#FFE6E6')
            table[(i, 1)].set_facecolor('#FFE6E6')

    # Alternate row colors
    for i in range(1, len(characters) + 1):
        if sorted_centrality[i - 1][0] != ego_character:
            if i % 2 == 0:
                table[(i, 0)].set_facecolor('#F0F0F0')
                table[(i, 1)].set_facecolor('#F0F0F0')

    # Title
    plt.title(f"{book_name}\nEigenvector Centrality in {ego_character.capitalize()}'s Network",
              fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved centrality table to {save_path}")
    plt.close()


def visualize_ego_network(ego_graph: nx.DiGraph, ego_character: str, book_name: str,
                          min_weight: int = 1, save_path: str = None, degree: float = 1.5):
    """
    Visualize an ego network with the ego node at the center.

    Parameters:
    -----------
    ego_graph : nx.DiGraph
        The ego network graph
    ego_character : str
        Name of the ego character
    book_name : str
        Name/title for the plot
    min_weight : int
        Minimum edge weight to display (filters weak connections)
    save_path : str
        If provided, saves the figure to this path
    degree : float
        1.0 for 1-degree, 1.5 for 1.5-degree (used in title)
    """
    if ego_graph.number_of_nodes() == 0:
        print(f"No network to visualize for {ego_character} in {book_name}")
        return

    # Filter edges by minimum weight
    edges_to_draw = [(u, v) for u, v, d in ego_graph.edges(data=True)
                     if d.get('weight', 1) >= min_weight]
    filtered_graph = ego_graph.edge_subgraph(edges_to_draw).copy()

    if filtered_graph.number_of_nodes() == 0:
        print(f"No edges meet minimum weight threshold of {min_weight}")
        return

    # Calculate eigenvector centrality for 1.5-degree networks
    centrality = {}
    if degree == 1.5 and filtered_graph.number_of_edges() > 0:
        try:
            # Use undirected graph for eigenvector centrality
            G_undirected = filtered_graph.to_undirected()
            centrality = nx.eigenvector_centrality(G_undirected, max_iter=1000, weight='weight')

            # Save centrality table as separate image
            if save_path:
                table_save_path = save_path.replace('.png', '_centrality.png')
                _save_centrality_table(centrality, ego_character, book_name, table_save_path)

            # print(f"\nEigenvector Centrality for {ego_character}'s network in {book_name}:")
            sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            # for char, cent in sorted_centrality:
                # print(f"  {char}: {cent:.4f}")
        except Exception as e:
            print(f"Could not compute eigenvector centrality for {book_name}: {e}")
            centrality = {}

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12))

    # Create layout with ego at center
    pos = {}
    other_nodes = [n for n in filtered_graph.nodes() if n != ego_character]

    # Place ego at center
    pos[ego_character] = (0, 0)

    # Sort nodes alphabetically for consistent positioning
    other_nodes_sorted = sorted(other_nodes)

    # Arrange other nodes in a circle around ego (consistent positions)
    import math
    n_others = len(other_nodes_sorted)
    if n_others > 0:
        for i, node in enumerate(other_nodes_sorted):
            angle = 2 * math.pi * i / n_others
            radius = 1.0
            pos[node] = (radius * math.cos(angle), radius * math.sin(angle))

    # Calculate interaction strength with ego for each node
    interaction_weights = {}
    for node in other_nodes_sorted:
        # Sum of incoming and outgoing edges between node and ego
        weight_to_ego = 0
        weight_from_ego = 0

        if filtered_graph.has_edge(node, ego_character):
            weight_to_ego = filtered_graph[node][ego_character].get('weight', 0)
        if filtered_graph.has_edge(ego_character, node):
            weight_from_ego = filtered_graph[ego_character][node].get('weight', 0)

        interaction_weights[node] = weight_to_ego + weight_from_ego

    # Calculate node sizes based on interaction with ego (consistent for both degrees)
    max_interaction = max(interaction_weights.values()) if interaction_weights else 1

    node_colors = []
    node_sizes = []
    for node in filtered_graph.nodes():
        if node == ego_character:
            node_colors.append('#FF3333')
            node_sizes.append(3000)
        else:
            node_colors.append('#3498DB')
            # Size proportional to interaction strength with ego
            interaction = interaction_weights.get(node, 0)
            if max_interaction == 0:
                max_interaction = 1
            size = 500 + (interaction / max_interaction) * 2000
            node_sizes.append(size)

    # Draw nodes
    nx.draw_networkx_nodes(filtered_graph, pos,
                           node_color=node_colors,
                           node_size=node_sizes,
                           alpha=0.9,
                           ax=ax)

    # Get edge weights for width scaling
    edges = list(filtered_graph.edges(data=True))
    weights = [d['weight'] for u, v, d in edges]
    max_weight = max(weights) if weights else 1

    # Draw edges with width proportional to weight
    edge_widths = [1 + 4 * w / max_weight for w in weights]
    nx.draw_networkx_edges(filtered_graph, pos,
                           width=edge_widths,
                           alpha=0.8,
                           edge_color='#000129',
                           arrows=True,
                           arrowsize=25,
                           arrowstyle='->',
                           connectionstyle='arc3,rad=0.1',
                           ax=ax)

    # Draw labels
    labels = nx.draw_networkx_labels(filtered_graph, pos,
                                     font_size=30,
                                     font_weight='bold',
                                     font_color='black',
                                     ax=ax)

    # Add edge weight labels for the top 5 highest-weight edges
    top_edges = sorted(filtered_graph.edges(data=True),
                       key=lambda x: x[2]['weight'], reverse=True)[:5]

    # Plot labels manually (supports bidirectional edges)
    for u, v, d in top_edges:
        weight = d['weight']

        # midpoint
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2

        # offset if bidirectional
        if filtered_graph.has_edge(v, u):
            dx = y2 - y1
            dy = x1 - x2
            norm = (dx ** 2 + dy ** 2) ** 0.5
            offset = 0.08 / norm if norm != 0 else 0
            mx += dx * offset
            my += dy * offset

        ax.text(mx, my, f"{weight}",
                fontsize=24, fontweight='bold', color='black',
                ha='center', va='center',
                path_effects=[path_effects.withStroke(linewidth=2, foreground='white')])

    # Title with degree information
    degree_str = "1-Degree" if degree == 1.0 else "1.5-Degree"
    title = f"{book_name}\n{ego_character.capitalize()}'s {degree_str} Ego Network"
    ax.set_title(title, fontsize=30, fontweight='bold', pad=20)
    ax.axis('off')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    plt.tight_layout()

    # Save or show
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()

    plt.close()


def visualize_character_ego_networks_per_book(character_name: str, min_weight: int = 1,
                                              degree: float = 1.5, save: bool = True):
    """
    Create visualizations of any character's ego network for each book.

    Parameters:
    -----------
    character_name : str
        Name of the character to visualize
    min_weight : int
        Minimum edge weight to display
    degree : float
        1.0 for 1-degree ego network (direct connections only)
        1.5 for 1.5-degree ego network (direct + inter-connections)
    save : bool
        If True, saves figures to files; if False, displays them
    """
    all_books = get_x_mentions_y_per_book()
    character_lower = character_name.lower()

    for book_number, book_data in enumerate(all_books, start=1):
        book_name = f"Book {book_number}: {BOOK_NAMES[book_number]}"

        # Extract ego network
        ego_data, ego_graph = _extract_ego_network(book_data, character_lower, radius=1, degree=degree)

        # Create save path if saving
        save_path = None
        if save:
            import os
            saving_path = "results/ego"
            os.makedirs(saving_path, exist_ok=True)
            degree_suffix = "1deg" if degree == 1.0 else "1.5deg"
            save_path = f"{saving_path}/{character_lower}_ego_{degree_suffix}_book_{book_number}.png"

        # Visualize (this will also create centrality table for 1.5-degree networks)
        visualize_ego_network(ego_graph, character_lower, book_name,
                              min_weight=min_weight, save_path=save_path, degree=degree)