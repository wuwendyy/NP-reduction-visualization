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
    three_sat_problem.load_formula(clauses)

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
    is_set = reduction.sol1tosol2(sat_assignment)
    print("Independent Set from SAT assignment:", is_set)

    recovered_assignment = reduction.sol2tosol1(is_set)
    print("Recovered SAT assignment:", recovered_assignment)

if __name__ == "__main__":
    main()
