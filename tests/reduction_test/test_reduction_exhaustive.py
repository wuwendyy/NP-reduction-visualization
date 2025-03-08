from itertools import product

# Import the classes from your existing code
from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction

def test_reduction_exhaustive(clauses):
    """
    Exhaustively tests that for every assignment:
      - If the formula is satisfied, the resulting set is indeed independent.

    This test re-creates the ThreeSATProblem, IndependentSetProblem, and
    the Reduction *from scratch* for each assignment. That way, 
    there's no leftover state between tests.
    """

    # 1) Collect all variable IDs from the clause list
    #    e.g. if clauses has var_ids = {1,2,3,4}, we find them by scanning the input
    var_ids_set = set()
    for clause in clauses:
        for (var_id, _negated) in clause:
            var_ids_set.add(var_id)
    var_ids = sorted(list(var_ids_set))

    print("\n[EXHAUSTIVE TEST] Variables:", var_ids)

    # 2) Generate all possible assignments for these variables
    all_combos = list(product([False, True], repeat=len(var_ids)))
    total_combos = len(all_combos)
    print(f"Total possible assignments: {total_combos}\n")

    mismatch_count = 0

    for combo in all_combos:
        # 3) Build a fresh 3-SAT problem from scratch
        three_sat_problem = ThreeSATProblem()
        three_sat_problem.load_formula(clauses)

        # 4) Build a fresh Independent Set problem
        ind_set_problem = IndependentSetProblem()

        # 5) Create a new reduction object
        reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem)

        # 6) Build the graph from the formula
        reduction.build_graph_from_formula()

        # 7) Construct the assignment dictionary from combo
        assignment = {}
        for i, var_id in enumerate(var_ids):
            assignment[var_id] = combo[i]

        # 8) Evaluate 3-SAT and check the resulting set
        satisfied = three_sat_problem.evaluate(assignment)
        node_set = reduction.sol1tosol2(assignment)
        is_independent = ind_set_problem.is_independent_set(node_set)

        # If formula is satisfied => set must be independent
        if satisfied and not is_independent:
            mismatch_count += 1
            print(f"[ERROR] Found a satisfying assignment => set is NOT independent!")
            print(f"  Assignment: {assignment}")
            print(f"  Node set: {node_set}\n")

    print("\nExhaustive test finished.")
    if mismatch_count == 0:
        print("SUCCESS: All satisfying assignments mapped to an independent set!")
    else:
        print(f"FAILURE: Found {mismatch_count} mismatch(es) where formula was satisfied but set not independent.")

if __name__ == "__main__":
    # Example formula to test
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]
    test_reduction_exhaustive(clauses)
