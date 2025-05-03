import pygame
import numpy as np

from npvis.element.element import Formula, Clause, Variable
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
    for clause in formula.get_as_list():
        clause_satisfied = False  # Clause must have at least one True literal

        for literal in clause:
            var = literal.name
            is_not_negated = literal.is_not_negated
            clause_id = literal.clause_id
            id = literal.id  # (i, False) → ¬x_i, (i, True) → x_i

            if sat_assignment.get(var, True) == is_not_negated:  # Check if this literal is True
                clause_satisfied = True
            elif sat_assignment.get(var, False) != is_not_negated:
                clause_satisfied = True

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

def construct_formula(clause_list):
        """
        Constructs a Formula object from a list of clauses.

        Args:
            clause_list (list): A list of clauses, where each clause is a list of tuples
                                (var_id, is_not_negated).

        Returns:
            Formula: A Formula object containing all the clauses.
        """
        formula_obj = Formula()
        
        lit_id = 1
        for clause_idx, clause in enumerate(clause_list, start=1):  # Clause IDs start from 1
            clause_obj = Clause(clause_idx)
            
            for var_id, is_not_negated in clause:
                variable = Variable(var_id, is_not_negated, clause_idx,  lit_id)
                print(variable)
                clause_obj.add_variable(variable)
                lit_id += 1  # Increment ID for each variable

            formula_obj.clauses.append(clause_obj)

        return formula_obj
                
if __name__ == "__main__":
    prim_formula = [
        [(1, False), (2, True), (3, True)],   # Clause 1: ( ¬x1 ∨ x2 ∨ x3 )
        [(1, True), (2, False), (3, True)],   # Clause 2: ( x2 ∨ x3 ∨ ¬x4 )
        [(1, False), (2, True), (4, True)]    # Clause 3: ( x1 ∨ ¬x2 ∨ x4 )
    ]

    formula = construct_formula(prim_formula)
    
    # print_formula(formula)
    
    reduction = ThreeSatToIndependentSetReduction(formula)

    # Extract necessary mappings
    graph = reduction.graph
    clause_vertices = reduction.clause_vertices
    literal_to_formula_indices = reduction.literal_to_formula_indices
    lit_to_node_id = reduction.lit_to_node_id
    literal_id_to_node_id = reduction.literal_id_to_node_id

    print("Literal ID to Node ID Mapping:")
    for literal, node in literal_id_to_node_id.items():
        print(f"Literal: {literal} → Node ID: {node}")


    # Print the mapping from literals to nodes
    print("\nLiteral to Node Mapping:")
    for (literal, clause_idx), node_id in lit_to_node_id.items():
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
            "ID": node.id,
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
    
    ### Hao: those are added for the visualization 
    # Define bounding boxes for both elements
    graph_bounding_box = np.array([[400, 50], [780, 550]])  # Right side of the window
    formula_bounding_box = np.array([[20, 50], [380, 200]])  # Left upper side
    graph.set_bounding_box(graph_bounding_box)
    graph.determine_node_positions()
    formula.set_bounding_box(formula_bounding_box)
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Graph and Formula Display")
    clock = pygame.time.Clock()
    
    # Main loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Display both elements
        graph.display(screen)
        formula.display(screen)

        pygame.display.flip()
        clock.tick(30)  # Limit FPS to 30

    pygame.quit()
