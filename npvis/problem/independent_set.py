from npvis.element import Graph, Node, Edge
from npvis.problem.np_problem import NPProblem

class IndependentSetProblem(NPProblem):
    """
    Manages the graph structure for an Independent Set problem.
    No visualization is handled here.
    """

    def __init__(self):
        super().__init__(Graph())
        self.next_node_id = 1

    def evaluate(self, node_ids) -> bool:
        """
        Checks if node_ids form an independent set in this graph.

        Args:
            node_ids (iterable): Collection of node IDs.

        Returns:
            bool: True if no two nodes in the set have an edge, else False.
        """
        node_ids = set(node_ids)
        for node1_id in node_ids:
            for node2_id in node_ids:
                if node1_id != node2_id and self.element.hasEdge(
                    self.element.get_node_by_id(node1_id), self.element.get_node_by_id(node2_id)
                ):
                    return False
        return True

    def get_graph(self) -> Graph:
        """
        Returns the underlying Graph object.
        """
        return self.element
    
    def set_solution_by_id(self, solution):
        independent_set = set()
        other_set = set()
        for node in self.element.nodes:
            node_id = node.id
            if node_id in solution:
                independent_set.add(node)
            else:
                other_set.add(node)
        sol = [independent_set, other_set]
        self.solution = sol
    
    def set_solution(self, solution):
        independent_set = set()
        other_set = set()
        for node in self.element.nodes:
            if node in solution:
                independent_set.add(node)
            else:
                other_set.add(node)
        sol = [independent_set, other_set]
        self.solution = sol



# if __name__ == "__main__":
#     ind_set_problem = IndependentSetProblem()
#     n1 = ind_set_problem.add_node("A")
#     n2 = ind_set_problem.add_node("B")
#     n3 = ind_set_problem.add_node("C")
#
#     ind_set_problem.add_edge(n1, n2)
#     ind_set_problem.add_edge(n2, n3)
#
#     test_set = {n1.id, n3.id}
#     print("Is it independent?", ind_set_problem.evaluate(test_set))  # Expect True
