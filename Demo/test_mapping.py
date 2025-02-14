import networkx as nx
import itertools
from element import Formula
from helpers import Node, Edge
from three_sat_reduction import ThreeSatToIndependentSetReduction

def test_build_graph(test_formula):
        # Create instance of the reduction
        reduction = ThreeSatToIndependentSetReduction(test_formula)
        
        # Call the function to test
        reduction._build_graph()

        # Print node mapping to check one-to-one relationship
        print("\n=== Node Mapping (One-to-One Check) ===")
        for (c_idx, lit_idx), node_id in reduction.node_mapping.items():
            print(f"Clause {c_idx}, Literal {lit_idx} → Node {node_id}")

        # Print assignment mapping to ensure correctness
        print("\n=== Assignment Mapping ===")
        for key, nodes in reduction.assignment_mapping.items():
            print(f"Literal {key}: Nodes {nodes}")

        # Print edges to ensure conflict constraints are correctly added
        print("\n=== Graph Edges ===")
        for edge in reduction.graph.edges():
            print(edge)
            
# Run the test
test_formula = Formula()
test_formula.clauses = [
    [(1, False), (2, True), (3, False)],
    [(2, False), (3, True), (4, False)],
    [(1, False), (2, True), (4, False)]
]
test_build_graph(test_formula)