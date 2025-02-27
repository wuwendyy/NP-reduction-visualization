from three_sat_reduction import ThreeSatToIndependentSetReduction


if __name__ == "__main__":
    formula = [
        [(1, False), (2, True), (3, False)],   # Clause 1: ( x1 ∨ ¬x2 ∨ x3 )
        [(2, False), (3, True), (4, False)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
        [(1, False), (2, True), (4, False)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    ]

    reduction = ThreeSatToIndependentSetReduction(formula)

    # Extract necessary mappings
    graph = reduction.graph
    clause_vertices = reduction.clause_vertices
    literal_to_formula_indices = reduction.literal_to_formula_indices
    literal_id_to_node_id = reduction.literal_id_to_node_id

    # Print the mapping from literals to nodes
    print("\nLiteral to Node Mapping:")
    for (literal, clause_idx), node_id in literal_id_to_node_id.items():
        print(f"Literal {literal} in Clause {clause_idx} -> Node ID {node_id}")

    # Print the literal_id to node_id mapping
    print("\nLiteral ID to Node ID Mapping:")
    for (literal, clause_idx), node_id in literal_id_to_node_id.items():
        print(f"Literal {literal} in Clause {clause_idx} -> Node ID {node_id}")

    # Ensure Clause 3 is included
    print("\nClause Vertices:")
    for idx, clause in enumerate(clause_vertices):
        print(f"Clause {idx + 1}: {clause}")

    # Print the graph nodes
    print("\nGraph Nodes (ID → Literal):")
    for node, data in graph.nodes(data=True):
        print(f"Node {node}: {data['literal']} (Clause {data['clause_index']})")

    # Print the graph edges
    print("\nGraph Edges:")
    for edge in graph.edges():
        print(edge)

    # Example assignment {x1=True, x2=False, x3=True, x4=False}
    sat_assignment = {1: True, 2: False, 3: True, 4: False}
    independent_set = reduction.sol1tosol2(sat_assignment)

    print("\nIndependent Set:", independent_set)

    recovered_assignment = reduction.sol2tosol1(independent_set)
    print("\nRecovered SAT Assignment:", recovered_assignment)

 
