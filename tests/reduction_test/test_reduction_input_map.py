import pygame
import numpy as np

from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction


def main():
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
    reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem, 1)

    # 4) Build graph from 3-SAT
    reduction.build_graph_from_formula()
    
    print("Completed input1_to_input2_dict: ")
    for key, value in reduction.input1_to_input2_dict.items():
        print(f"{key} : {value}")

    # 5) Example assignment
    sat_assignment = {1: True, 2: True, 3: False, 4: False}

    # 6) # Convert solutions
    is_set = reduction.solution1_to_solution2(sat_assignment)
    print("Independent Set from SAT assignment:", is_set)

    recovered_assignment = reduction.solution2_to_solution1(is_set)
    print("Recovered SAT assignment:", recovered_assignment)
    print("Conversion to SAT Assignment completed!\n")


if __name__ == "__main__":
    main()
