import numpy as np
from npvis.game_manager import GameManager

def main():
    # 1) Create problems
    from npvis.problem import ThreeSATProblem, ThreeColoringProblem
    from npvis.reduction import ThreeSatToThreeColoringReduction

    three_sat = ThreeSATProblem()
    three_col = ThreeColoringProblem()

    # 2) Load a CNF formula into ThreeSATProblem
    clauses = [
        [(1, False), (2, True),  (3, True )],  # (¬x1 ∨ x2 ∨ x3)
        [(1, True ), (2, False), (3, True )],  # ( x1 ∨ ¬x2 ∨ x3)
        [(1, False), (2, True),  (4, True )]   # (¬x1 ∨ x2 ∨ x4)
    ]
    three_sat.load_formula_from_tuples(clauses)
    # three_sat.load_formula_from_file("data/sampleFormula.txt")  # Provide correct file path

    # 3) Create and build the reduction
    reduction = ThreeSatToThreeColoringReduction(three_sat, three_col, debug=False)
    reduction.build_graph_from_formula()

    # 4) Pick an example SAT assignment
    sat_assignment = {1: True, 2: True, 3: False, 4: False}

    # 5) Test forward & reverse
    sat_ok, col_ok = reduction.test_solution(sat_assignment)
    print("Formula satisfied?", sat_ok)
    print("Graph 3‑coloring valid?", col_ok)

    # 6) Compute the coloring from the SAT assignment
    color_sets = reduction.solution1_to_solution2(sat_assignment)
    print("Coloring sets:", [ {n.id for n in s} for s in color_sets ])
    three_col.set_solution(color_sets)

    # 7) Recover SAT assignment from the coloring
    recovered = reduction.solution2_to_solution1(color_sets)
    print("Recovered SAT assignment:", recovered)
    three_sat.set_solution(recovered)

    # 8) Launch the interactive display
    gm = GameManager(width=1200, height=800, fps=30)
    formula_bb = np.array([[20,  50], [380, 750]])  # left pane
    graph_bb   = np.array([[420, 50], [1180, 750]])  # right pane

    gm.add_problem(three_sat, formula_bb)
    gm.add_problem(three_col, graph_bb)
    gm.add_reduction(reduction)   # so clicking literals/nodes highlights correspondences
    gm.run()

if __name__ == "__main__":
    main()
