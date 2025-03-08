"""
Tests for the IndependentSetProblem class.
Run via:  python test_independent_set_problem.py
"""
from npvis.problem.independent_set import IndependentSetProblem

def test_simple_graph():
    """
    Test a simple chain of nodes: A - B - C
    The set {A, C} should be independent, but {A, B} is not.
    """
    print("\n[TEST] Simple Graph")
    problem = IndependentSetProblem()

    A = problem.add_node("A")
    B = problem.add_node("B")
    C = problem.add_node("C")

    problem.add_edge(A, B)
    problem.add_edge(B, C)

    # {A, C} is an independent set => True
    test_set = {A.node_id, C.node_id}
    assert problem.is_independent_set(test_set) is True, "A,C should be independent"

    # {A, B} is not independent => there's an edge
    test_set2 = {A.node_id, B.node_id}
    assert problem.is_independent_set(test_set2) is False, "A,B share an edge => not independent"

    print("Simple graph test passed!")


def test_group_function():
    """
    Test adding a group of nodes in one shot.
    """
    print("\n[TEST] Groups")
    problem = IndependentSetProblem()

    n1 = problem.add_node("1")
    n2 = problem.add_node("2")
    problem.add_group([n1, n2])  # Should succeed

    # Next test: try an invalid group (duplicate node)
    try:
        problem.add_group([n1, n1])
        assert False, "Expected AssertionError due to duplicates"
    except AssertionError:
        print("Caught expected AssertionError for duplicate nodes in group.")

    # Another invalid group: Node not in graph
    from npvis.element.element import Node
    weird_node = Node(999, "X")
    try:
        problem.add_group([weird_node])
        assert False, "Expected AssertionError for node not in graph"
    except AssertionError:
        print("Caught expected AssertionError for node not in graph.")
    
    print("Group function tests passed!")


def test_edge_validation():
    """
    Ensure add_edge() fails if we do something invalid,
    e.g. edge to the same node or with a node not in the graph.
    """
    print("\n[TEST] Edge Validation")
    problem = IndependentSetProblem()

    nA = problem.add_node("A")
    try:
        problem.add_edge(nA, nA)
        assert False, "Expected error adding edge between same node."
    except AssertionError:
        print("Caught expected AssertionError for same-node edge.")
    
    from npvis.element.element import Node
    alien_node = Node(999, "alien")
    try:
        problem.add_edge(nA, alien_node)
        assert False, "Expected error adding edge with a node not in the graph."
    except AssertionError:
        print("Caught expected AssertionError for node not in the graph.")

    # Valid edge
    nB = problem.add_node("B")
    problem.add_edge(nA, nB)
    print("Edge validation tests passed!")


def main():
    test_simple_graph()
    test_group_function()
    test_edge_validation()
    print("\nAll IndependentSetProblem tests passed!")

if __name__ == "__main__":
    main()
