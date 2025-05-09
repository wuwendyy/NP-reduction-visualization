import numpy as np
from npvis.game_manager import GameManager
from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction


def main():
    # 1) Create problems
    three_sat = ThreeSATProblem()
    ind_set = IndependentSetProblem()
    
    # 2) Load a CNF formula into ThreeSATProblem
    clauses = [
        [('x1', False), ('x2', True),  ('x3', True )],  # (¬x1 ∨ x2 ∨ x3)
        [('x1', True ), ('x2', False), ('x3', True )],  # ( x1 ∨ ¬x2 ∨ x3)
        [('x1', False), ('x2', True),  ('x4', True )]   # (¬x1 ∨ x2 ∨ x4)
    ]
    three_sat.load_formula_from_tuples(clauses)
    # three_sat.load_formula_from_file("sampleFormula.txt")  # Provide correct file path
    
    # 3) Create and build the reduction
    reduction = ThreeSatToIndependentSetReduction(three_sat, ind_set, debug=False) # debug Flag
    reduction.input1_to_input2()
    
    # 4) Pick an example SAT assignment
    sat_assignment = {'x1': True, 'x2': True, 'x3': False, 'x4': False}
    reduction.problem1.solution = sat_assignment
    
    # 5) Test forward & reverse
    sat_ok, ind_set_ok = reduction.test_solution(sat_assignment)
    print("Formula satisfied?", sat_ok)
    print("Graph independent set valid?", ind_set_ok)
    
    # 6) Compute the independent set from the SAT assignment
    is_set = reduction.solution1_to_solution2()
    print("Independent Set from SAT assignment:", is_set)
    ind_set.set_solution(is_set)
    
    # 7) Recover SAT assignment from the independent set
    recovered = reduction.solution2_to_solution1(is_set)
    print("Recovered SAT assignment:", recovered)
    three_sat.set_solution(recovered)
    
    # 8) Launch the interactive display
    gm = GameManager(width=1200, height=800, fps=30)
    formula_bb = np.array([[20,  50], [380, 750]])  # left pane
    graph_bb   = np.array([[420, 50], [1180, 750]])  # right pane
    
    gm.add_problem(three_sat, formula_bb)
    gm.add_problem(ind_set, graph_bb)
    gm.add_reduction(reduction)   # so clicking literals/nodes highlights correspondences
    gm.run()
    
if __name__ == "__main__":
    main()
    