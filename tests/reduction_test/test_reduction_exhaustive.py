from itertools import product
from itertools import combinations

from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction

def test_reduction_forward(clauses):
    """
    Test: If a given SAT assignment satisfies the formula, 
          then the resulting node set (sol1tosol2) must be independent.

    For each assignment, we:
      1) Recreate ThreeSATProblem, IndependentSetProblem, and the Reduction.
      2) If the formula is satisfied => the node set must be independent.
    """

    # Collect variables from the clauses
    var_ids = sorted({var_id for clause in clauses for (var_id, _) in clause})
    all_combos = list(product([False, True], repeat=len(var_ids)))

    mismatch_count = 0
    total_checked = 0

    for combo in all_combos:
        # Build fresh problems each time
        three_sat_problem = ThreeSATProblem()
        three_sat_problem.load_formula(clauses)
        ind_set_problem = IndependentSetProblem()
        reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem)

        # Build the graph
        reduction.build_graph_from_formula()

        # Construct assignment
        assignment = {var_ids[i]: combo[i] for i in range(len(var_ids))}

        satisfied = three_sat_problem.evaluate(assignment)
        if satisfied:
            # If satisfied => the set must be independent
            node_set = reduction.solution1_to_solution2(assignment)
            is_indep = ind_set_problem.evaluate(node_set)
            if not is_indep:
                mismatch_count += 1
                print(f"[ERROR] Satisfied => set is NOT independent!")
                print(f"  Assignment: {assignment}, Node set: {node_set}")

        total_checked += 1

    print(f"\n--- Forward Test Results ---")
    print(f"Total assignments checked: {total_checked}")
    if mismatch_count == 0:
        print("SUCCESS: All satisfying assignments mapped to independent sets.")
    else:
        print(f"FAILURE: Found {mismatch_count} mismatch(es) in forward direction.")

def test_reduction_reverse(clauses):
    """
    Reverse-direction test: If there's an independent set of size = number_of_clauses,
    then the recovered assignment must satisfy the formula.

    1) Build the 3-SAT problem and the IS problem exactly once.
    2) Build the graph from the formula (the node IDs won't change).
    3) Enumerate all subsets of node IDs of size=#clauses. If a subset is independent,
       call sol2tosol1() => must satisfy the formula.
    """

    # Step 1: Create problems and build once
    three_sat_problem = ThreeSATProblem()
    three_sat_problem.load_formula(clauses)
    ind_set_problem = IndependentSetProblem()
    reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem)
    reduction.build_graph_from_formula()

    num_clauses = len(clauses)
    if num_clauses == 0:
        print("No clauses => trivial case.")
        return

    # Gather node IDs from the built graph
    node_ids = [n.id for n in ind_set_problem.get_graph().nodes]
    node_ids.sort()

    mismatch_count = 0
    total_checked = 0

    # Step 2: For each subset of node IDs of size = #clauses
    for subset in combinations(node_ids, num_clauses):
        subset_set = set(subset)
        # Check independence
        if ind_set_problem.evaluate(subset_set):
            # Then the recovered assignment must satisfy the formula
            assignment = reduction.solution2_to_solution1(subset_set)
            satisfied = three_sat_problem.evaluate(assignment)
            if not satisfied:
                mismatch_count += 1
                print(f"[ERROR] Independent set => formula not satisfied!")
                print(f"  Subset={subset_set}, Recovered assignment={assignment}")
        total_checked += 1

    print("\n=== Reverse-Direction Test ===")
    print(f"Checked {total_checked} subsets of size={num_clauses}.")
    if mismatch_count == 0:
        print("SUCCESS: All independent sets correspond to satisfying assignments.")
    else:
        print(f"FAILURE: Found {mismatch_count} mismatch(es).")

def main():
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]

    print("\n===== FORWARD DIRECTION TEST =====")
    test_reduction_forward(clauses)

    print("\n===== REVERSE DIRECTION TEST =====")
    test_reduction_reverse(clauses)

if __name__ == "__main__":
    main()
