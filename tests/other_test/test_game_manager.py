import numpy as np
from npvis.game_manager import GameManager

def main():
    from npvis.problem import ThreeSATProblem, IndependentSetProblem
    from npvis.reduction import ThreeSatToIndependentSetReduction

    # 1) Create problems
    three_sat_problem = ThreeSATProblem()
    ind_set_problem = IndependentSetProblem()

    # 2) Load formula into ThreeSATProblem
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]
    three_sat_problem.load_formula_from_tuples(clauses)

    # 3) Create the reduction
    reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem)

    # 4) Build graph from 3-SAT
    reduction.build_graph_from_formula()

    # 5) Example assignment
    sat_assignment = {1: True, 2: True, 3: False, 4: False}

    # 6) Check solution
    satisfied, is_valid = reduction.test_solution(sat_assignment)
    print("Is 3-SAT satisfied?", satisfied)
    print("Is the corresponding set an independent set?", is_valid)

    # Convert solutions
    is_set = reduction.solution1_to_solution2(sat_assignment)
    print("Independent Set from SAT assignment:", is_set)
    ind_set_problem.set_solution(is_set)

    recovered_assignment = reduction.solution2_to_solution1(is_set)
    print("Recovered SAT assignment:", recovered_assignment)
    
    three_sat_problem.set_solution(recovered_assignment)

    # Create GameManager instance
    gm = GameManager(width=800, height=600, fps=30)
    # Define bounding boxes for the problems (for example, formula on left, graph on right)
    formula_bounding_box = np.array([[20, 50], [380, 550]])
    graph_bounding_box = np.array([[420, 50], [780, 550]])

    gm.add_problem(three_sat_problem, formula_bounding_box)
    gm.add_problem(ind_set_problem, graph_bounding_box)

    gm.add_reduction(reduction)

    gm.run()

if __name__ == "__main__":
    main()
