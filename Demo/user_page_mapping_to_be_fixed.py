import sys
from element import Graph, Formula
from helpers import Node, Edge
from three_sat_reduction import ThreeSatToIndependentSetReduction
from three_sat_visualizer import ThreeSatGraphVisualizer
import itertools

# Example Formula
formula = Formula()
formula.clauses = [
    [(1, False), (2, True), (3, False)],
    [(2, False), (3, True), (4, False)],
    [(1, False), (2, True), (4, False)]
]

# Step 1: Reduce 3-SAT to Independent Set Graph
reduction = ThreeSatToIndependentSetReduction(formula)
G, clause_vertices, formula, literal_to_formula_indices = reduction.build_3sat_graph_from_formula()

# Step 2: Visualize
visualizer = ThreeSatGraphVisualizer(
    graph=G,
    clause_vertices=clause_vertices,
    formula=formula,
    literal_to_formula_indices=literal_to_formula_indices
)

visualizer.run()

# Step 3: Convert SAT assignment to Independent Set
sat_assignment = {1: True, 2: False, 3: True, 4: False}
independent_set = reduction.sol1tosol2(sat_assignment)
print("Independent Set Solution:", independent_set)

# Step 4: Convert Independent Set back to SAT assignment
reconstructed_assignment = reduction.sol2tosol1(independent_set)
print("Reconstructed SAT Assignment:", reconstructed_assignment)