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
    node_id = 1

    # Example 3-SAT formula
    formula = [
        [(1, False), (2, True), (3, False)],   # Clause 1: ( x1 ∨ ¬x2 ∨ x3 )
        [(2, False), (3, True), (4, False)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
        [(1, False), (2, True), (4, False)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    ]

    # Track formula index for highlighting literals when clicking edges
    literal_to_formula_indices = {}
    literal_and_node = []
    literal_id_to_node_id = {}

    for c_idx, clause in enumerate(formula):
        print(f"Processing Clause {c_idx + 1}: {clause}")
        c_nodes = []
        
        for lit_idx, literal in enumerate(clause):
            print(f"Processing Literal: {literal}")
            G.add_node(node_id, literal=literal, clause_index=c_idx)
            c_nodes.append(node_id)
            literal_and_node.append((literal, node_id))
            literal_id_to_node_id[(literal, c_idx)] = node_id
            
            # Store formula index mapping for highlighting literals
            if literal not in literal_to_formula_indices:
                literal_to_formula_indices[literal] = []
            literal_to_formula_indices[literal].append((c_idx, lit_idx))
            
            node_id += 1

        # Ensure each clause forms a triangle by adding edges
        if len(c_nodes) == 3:
            G.add_edges_from([(c_nodes[0], c_nodes[1]), (c_nodes[1], c_nodes[2]), (c_nodes[2], c_nodes[0])])
        elif len(c_nodes) == 2:
            G.add_edge(c_nodes[0], c_nodes[1])

        clause_vertices.append(c_nodes)

    # ✅ DEBUG: Print all edges to verify they exist
    print("\nNodes in the graph (ID → Literal):")
    for node, data in G.nodes(data=True):
        print(f"Node {node}: {data['literal']} (Clause {data['clause_index']})")
    
    for c_idx in range(len(formula) - 1):  # Check neighboring clauses
        for literal in formula[c_idx]:
            opposite_literal = (literal[0], not literal[1])  # Flip negation
            if opposite_literal in formula[c_idx + 1]:
                node1 = literal_id_to_node_id.get((literal, c_idx))
                node2 = literal_id_to_node_id.get((opposite_literal, c_idx + 1))
                if node1 is not None and node2 is not None:
                    if not G.has_edge(node1, node2):  # Avoid duplicate edges
                        G.add_edge(node1, node2)
                        print(f"Added negation edge: {literal} (Clause {c_idx}) ↔ {opposite_literal} (Clause {c_idx + 1}) (Nodes {node1} ↔ {node2})")
                        # print(f"Added negation edge: {literal} ↔ {opposite_literal} (Nodes {node1} ↔ {node2})")
    return G, clause_vertices, formula, literal_to_formula_indices, literal_and_node, literal_id_to_node_id


if __name__ == "__main__":
   
    # Build the 3-SAT graph
    graph, clause_vertices, formula, literal_to_formula_indices, literal_and_node, literal_id_to_node_id = build_3sat_graph()

    # Print the mapping from literals to nodes
    print("\nLiteral to Node Mapping:")
    for literal, node in literal_and_node:
        print(f"Literal {literal} -> Node {node}")

    # Print the literal_id to node_id mapping
    print("\nLiteral ID to Node ID Mapping:")
    for (literal, clause_idx), node_id in literal_id_to_node_id.items():
        print(f"Literal {literal} in Clause {clause_idx} -> Node ID {node_id}")

    # Ensure Clause 3 is included
    print("\nClause Vertices:")
    for idx, clause in enumerate(clause_vertices):
        print(f"Clause {idx + 1}: {clause}")
        
    # # # ✅ No need to pass 'width' as a separate parameter
    # visualizer = ThreeSatGraphVisualizer(
    #     graph=graph,
    #     clause_vertices=clause_vertices,
    #     formula=formula,
    #     literal_to_formula_indices=literal_to_formula_indices,
    #     literal_id_to_node_id = literal_id_to_node_id
    # )
    
    # # visualizer.run()
    
