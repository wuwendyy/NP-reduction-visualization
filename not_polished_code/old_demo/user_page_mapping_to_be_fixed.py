import sys
from npvis.element.element import Graph, Formula
from three_sat_reduction import ThreeSatToIndependentSetReduction
from three_sat_visualizer import ThreeSatGraphVisualizer

# Example Formula
formula = Formula()
formula.clauses = [ #(var, is_negated, clause_idx) 
    [(1, False, 1), (2, True, 1), (3, False, 1)],
    [(2, False, 2), (3, True, 2), (4, False, 2)],
    [(1, False, 3), (2, True, 3), (4, False, 3)]
]


# Step 1: Reduce 3-SAT to Independent Set Graph
reduction = ThreeSatToIndependentSetReduction(formula)
G, clause_vertices, formula, literal_to_formula_indices = reduction.build_3sat_graph_from_formula()

# Step 2: Visualize
visualizer = ThreeSatGraphVisualizer(
    graph=G,
    clause_vertices=clause_vertices,
    formula=formula,
    literal_to_formula_indices=literal_to_formula_indices,
    reduction = reduction
)

# visualizer.run()

sat_assignment = {1: 1, 2: 0, 3: 1, 4: 1}
visualizer.show_mapping(sat_assignment)

# # Step 3: Convert SAT assignment to Independent Set
# sat_assignment = {1: True, 2: False, 3: True, 4: False}
# independent_set = reduction.sol1tosol2(sat_assignment)
# print("Independent Set Solution:", independent_set)

# # Step 4: Convert Independent Set back to SAT assignment
# reconstructed_assignment = reduction.sol2tosol1(independent_set)
# print("Reconstructed SAT Assignment:", reconstructed_assignment)