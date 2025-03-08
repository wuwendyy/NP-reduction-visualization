"""
Tests for the ThreeSATProblem class.
Run via:  python test_three_sat_problem.py
"""
from npvis.problem.three_sat import ThreeSATProblem

def test_single_clause():
    """
    Test ThreeSATProblem with a single clause.
    Clause: (¬x1 ∨ x2) => Clause: [(1, False), (2, True)]
    """
    print("\n[TEST] Single Clause")
    problem = ThreeSATProblem()
    problem.load_formula([
        [(1, False), (2, True)]
    ])

    # Evaluate some assignments
    # 1) x1=False, x2=True => Satisfied
    assignment_1 = {1: False, 2: True}
    assert problem.evaluate(assignment_1) is True, "Should satisfy the clause"

    # 2) x1=False, x2=False => Satisfied (because x1=False matches ¬x1)
    assignment_2 = {1: False, 2: False}
    assert problem.evaluate(assignment_2) is True, "Should satisfy via ¬x1"

    # 3) x1=True, x2=False => Not satisfied
    assignment_3 = {1: True, 2: False}
    assert problem.evaluate(assignment_3) is False, "Neither literal is satisfied"

    print("Single clause tests passed!")


def test_multi_clause():
    """
    Test ThreeSATProblem with multiple clauses.
    Formula: (¬x1 ∨ x2 ∨ x3) ∧ (x1 ∨ ¬x2 ∨ x3)
    """
    print("\n[TEST] Multiple Clauses")
    problem = ThreeSATProblem()
    problem.load_formula([
        [(1, False), (2, True), (3, True)],  # (¬x1 ∨ x2 ∨ x3)
        [(1, True), (2, False), (3, True)]   # (x1 ∨ ¬x2 ∨ x3)
    ])

    # Evaluate some assignments
    # 1) x1=True, x2=True, x3=False => 
    #    Clause 1 => ¬x1? No (x1= True => ¬x1= false), x2= True => literal is true => Clause 1 satisfied
    #    Clause 2 => x1= True => literal is true => Clause 2 satisfied => entire formula => True
    assignment_1 = {1: True, 2: True, 3: False}
    assert problem.evaluate(assignment_1) is True, "Formula should be satisfied"

    # 2) x1=False, x2=False, x3=False =>
    #    Clause 1 => (¬x1= True, x2= false, x3= false) => Clause 1 satisfied by ¬x1
    #    Clause 2 => (x1= false => literal false, ¬x2= true => oh wait, x2=false => ¬x2= true => Clause 2 satisfied)
    #    entire formula => True
    assignment_2 = {1: False, 2: False, 3: False}
    assert problem.evaluate(assignment_2) is True, "Formula should be satisfied"

    # 3) x1=True, x2=False, x3=False =>
    #    Clause 1 => (¬x1= false, x2= false, x3= false) => Clause 1 is false
    #    Clause 2 => (x1= true => literal true => Clause 2 is true)
    #    entire formula => (false ∧ true) => false
    assignment_3 = {1: True, 2: False, 3: False}
    assert problem.evaluate(assignment_3) is False, "Formula should be unsatisfied"

    print("Multi-clause tests passed!")


def test_get_variables():
    """
    Test if get_variables() accurately returns all variables.
    """
    print("\n[TEST] get_variables()")
    problem = ThreeSATProblem()
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)]
    ]
    problem.load_formula(clauses)
    vars_collected = problem.get_variables()
    expected = {1, 2, 3}
    assert vars_collected == expected, f"Expected {expected}, got {vars_collected}"
    print("get_variables() test passed!")


def main():
    test_single_clause()
    test_multi_clause()
    test_get_variables()
    print("\nAll ThreeSATProblem tests passed!")

if __name__ == "__main__":
    main()
