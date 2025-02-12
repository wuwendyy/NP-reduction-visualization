import pygame
import networkx as nx
import math
from three_sat_visualizer import ThreeSatGraphVisualizer


# Screen settings
WIDTH, HEIGHT = 1000, 700  # Increase height to fit the formula text
BACKGROUND_COLOR = (255, 255, 255)  # White background
NODE_COLOR = (50, 100, 255)  # Blue nodes
EDGE_COLOR = (0, 0, 0)  # Black edges
HIGHLIGHT_COLOR = (255, 0, 0)  # Red for highlighting edges in the formula
RADIUS = 25


def build_3sat_graph():
    """
    Example function: Convert 3-SAT clauses into a graph where each clause forms a triangle.
    """
    G = nx.Graph()  # Create a NetworkX graph
    clause_vertices = []
    literal_to_node = {}
    node_id = 0

    # Example 3-SAT formula
    formula = [
        [(1, False), (2, True), (3, False)],   # Clause 1: ( x1 ∨ ¬x2 ∨ x3 )
        [(2, False), (3, True), (4, False)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
        [(1, False), (2, True), (4, False)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    ]

    # Track formula index for highlighting literals when clicking edges
    literal_to_formula_indices = {}

    for c_idx, clause in enumerate(formula):
        c_nodes = []
        
        for lit_idx, literal in enumerate(clause):
            G.add_node(node_id, literal=literal, clause_index=c_idx)
            c_nodes.append(node_id)

            # Store formula index mapping for highlighting literals
            if literal not in literal_to_formula_indices:
                literal_to_formula_indices[literal] = []
            literal_to_formula_indices[literal].append((c_idx, lit_idx))

            node_id += 1

        # **Ensure each clause forms a triangle by adding edges**
        if len(c_nodes) == 3:
            G.add_edges_from([(c_nodes[0], c_nodes[1]), (c_nodes[1], c_nodes[2]), (c_nodes[2], c_nodes[0])])
        elif len(c_nodes) == 2:
            G.add_edge(c_nodes[0], c_nodes[1])

        clause_vertices.append(c_nodes)

    # ✅ DEBUG: Print all edges to verify they exist
    # ✅ Print node structure (to view all assigned literals)
    print("\nNodes in the graph (ID → Literal):")
    for node, data in G.nodes(data=True):
        print(f"Node {node}: {data['literal']} (Clause {data['clause_index']})")
    
    # ✅ Add edges manually between opposite literals (`x ↔ ¬x`)
    for node1, data1 in G.nodes(data=True):
        lit1 = data1["literal"]
        opposite_literal = (lit1[0], not lit1[1])  # Flip negation

        # Find the node with the opposite literal
        for node2, data2 in G.nodes(data=True):
            if data2["literal"] == opposite_literal and node1 != node2:
                if not G.has_edge(node1, node2):  # Avoid duplicate edges
                    G.add_edge(node1, node2)
                    print(f"Added negation edge: {lit1} ↔ {opposite_literal} (Nodes {node1} ↔ {node2})")

    return G, clause_vertices, formula, literal_to_formula_indices

    # """
    # Builds a 3-SAT clause graph with:
    # - Clause triangles
    # - Negation edges (x ↔ ¬x)
    # - Mapping for formula highlighting
    # """
    # G = nx.Graph()  # Create an empty NetworkX graph
    # clause_vertices = []
    # literal_to_node = {}  # Maps literals (var, negated) → node_id
    # node_id = 0

    # # Example 3-SAT formula
    # formula = [
    #     [(1, False), (2, True), (3, False)],   # Clause 1: ( x1 ∨ ¬x2 ∨ x3 )
    #     [(2, False), (3, True), (4, False)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
    #     [(1, False), (2, True), (4, False)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    # ]

    # # Store mapping for highlighting formula
    # literal_to_formula_indices = {}  # (var, neg) → [indices in formula]

    # for c_idx, clause in enumerate(formula):
    #     c_nodes = []

    #     for lit_idx, literal in enumerate(clause):
    #         var_index, is_negated = literal

    #         # Store formula index mapping for highlighting
    #         if literal not in literal_to_formula_indices:
    #             literal_to_formula_indices[literal] = []
    #         literal_to_formula_indices[literal].append((c_idx, lit_idx))

    #         # Ensure each literal has only **one node** in the graph
    #         if literal in literal_to_node:
    #             node = literal_to_node[literal]
    #         else:
    #             G.add_node(node_id, literal=literal, clause_index=c_idx)
    #             literal_to_node[literal] = node_id
    #             node = node_id
    #             node_id += 1

    #         c_nodes.append(node)

    #     # Connect the 3 literals in this clause (triangle)
    #     if len(c_nodes) == 3:
    #         G.add_edges_from([(c_nodes[0], c_nodes[1]), (c_nodes[1], c_nodes[2]), (c_nodes[2], c_nodes[0])])
    #     elif len(c_nodes) == 2:
    #         G.add_edge(c_nodes[0], c_nodes[1])

    #     clause_vertices.append(c_nodes)

    # # Add edges between negations (x ↔ ¬x)
    # for (var, is_neg1), node1 in literal_to_node.items():
    #     negated_literal = (var, not is_neg1)  # Flip negation
    #     if negated_literal in literal_to_node:
    #         node2 = literal_to_node[negated_literal]
    #         G.add_edge(node1, node2)  # Connect x and ¬x

    # return G, clause_vertices, formula, literal_to_formula_indices



if __name__ == "__main__":
    # Build the 3-SAT graph
    G, clause_vertices, formula, literal_to_formula_indices = build_3sat_graph()

    # ✅ No need to pass 'width' as a separate parameter
    visualizer = ThreeSatGraphVisualizer(
        graph=G,
        clause_vertices=clause_vertices,
        formula=formula,
        literal_to_formula_indices=literal_to_formula_indices
    )
    
    visualizer.run()

