from three_sat_reduction import ThreeSatToIndependentSetReduction

def evaluate_formula(formula, sat_assignment):
    """
    Evaluates whether a given CNF formula is satisfied by a variable assignment.

    :param formula: List of clauses, where each clause is a list of literals (var_id, polarity).
                    Example: [[(1, False), (2, True)], [(3, False)]]
    :param sat_assignment: Dictionary mapping variable IDs to boolean values.
                    Example: {1: True, 2: False, 3: True}
    :return: bool, True if the formula is satisfied, False otherwise.
    """
    for clause in formula:
        clause_satisfied = False  # Clause must have at least one True literal

        for var, polarity in clause:
            if sat_assignment.get(var, False) == polarity:  # Check if this literal is True
                clause_satisfied = True
                break  # No need to check more literals in this clause

        if not clause_satisfied:
            return False  # If any clause is False, formula is False

    return True  # All clauses satisfied

def print_formula(formula):
    """
    Prints the CNF formula in a human-readable logical notation.
    
    :param formula: List of clauses, where each clause is a list of literals (var_id, polarity).
                    Example: [[(1, False), (2, True)], [(3, False)]]
    """
    formula_str = []
    
    for clause in formula:
        clause_str = []
        for var, polarity in clause:
            literal = f"¬x{var}" if not polarity else f"x{var}"
            clause_str.append(literal)
        
        formula_str.append(f"({' ∨ '.join(clause_str)})")  # Join literals with "OR"
    
    print(" ∧ ".join(formula_str))  # Join clauses with "AND"


if __name__ == "__main__":
    formula = [
        [(1, False), (2, True), (3, True)],   # Clause 1: ( ¬x1 ∨ x2 ∨ x3 )
        [(1, True), (2, False), (3, True)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
        [(1, False), (2, True), (4, True)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    ]

    print_formula(formula)
    
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
    # print("\nGraph Nodes (ID → Literal):")
    # for node, data in graph.nodes(data=True):
    #     print(f"Node {node}: {data['literal']} (Clause {data['clause_index']})")
    print("\nGraph Nodes (Detailed Info):")
    for node in graph.nodes:
        node_info = {
            "ID": node.node_id,
            "Literal": node.name,
            "Color": node.color,
            "Location": node.location.tolist(),  # Convert numpy array to list
            "Neighbors": node.neighbors
        }
        print(node_info)

    
    # Print the graph edges
    print("\nGraph Edges:")
    for edge in graph.edges:  # No () since `edges` is a set
        print(f"Edge between {edge.node1.name} and {edge.node2.name}, Color: {edge.color}")


    # Example assignment {x1=True, x2=False, x3=True, x4=False}
    sat_assignment = {1: True, 2: True, 3: False, 4: False}
    independent_set = reduction.sol1tosol2(sat_assignment)

    print("\nIndependent Set:", independent_set)

    recovered_assignment = reduction.sol2tosol1(independent_set)
    print("\nRecovered SAT Assignment:", recovered_assignment)

    IS_result = reduction.is_independent_set(independent_set)

    print("\nIs it an independent set?", IS_result)

    formula_result = evaluate_formula(formula, sat_assignment)
    
    print("\nDoes the formula evaluate to True?", formula_result)