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

    def add_node(self, name=None) -> Node:
        """
        Adds a node to the graph and returns it.

        Args:
            name (str): Optional name/label for the node.

        Returns:
            Node: The newly created node.
        """
        assert name == None or isinstance(name, str), "Name must be a string."
        assert len(name) <= 10, "Name must be at most 10 characters long."
        
        node_name = name if name else str(self.next_node_id)
        node = Node(self.next_node_id, node_name)
        self.element.add_node(node)
        self.next_node_id += 1
        return node

    def add_edge(self, node1, node2) -> None:
        """
        Adds an edge between two nodes in the graph.
        """
        assert node1 != None, "Node 1 is None."
        assert node2 != None, "Node 2 is None."
        assert node1 != node2, "Cannot add an edge between the same node."
        assert node1 in self.element.nodes, "Node 1 is not in the graph."
        assert node2 in self.element.nodes, "Node 2 is not in the graph."
        
        edge = Edge(node1, node2)
        self.element.add_edge(edge)
        
    def add_group(self, nodes) -> None:
        """
        Adds a group of nodes to the graph.
        """
        assert len(nodes) > 0, "Group must contain at least one node."
        assert len(set(nodes)) == len(nodes), "Group contains duplicate nodes."
        for node in nodes:
            assert node in self.element.nodes, "Node is not in the graph."
        
        self.element.groups.append(nodes)

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
        indepent_set = set()
        other_set = set()
        for node in self.element.nodes:
            node_id = node.id
            if node_id in solution:
                indepent_set.add(node)
            else:
                other_set.add(node)
        sol = [indepent_set, other_set]
        self.solution = sol
    
    def set_solution(self, solution):
        indepent_set = set()
        other_set = set()
        for node in self.element.nodes:
            if node in solution:
                indepent_set.add(node)
            else:
                other_set.add(node)
        sol = [indepent_set, other_set]
        self.solution = sol



if __name__ == "__main__":
    ind_set_problem = IndependentSetProblem()
    n1 = ind_set_problem.add_node("A")
    n2 = ind_set_problem.add_node("B")
    n3 = ind_set_problem.add_node("C")

    ind_set_problem.add_edge(n1, n2)
    ind_set_problem.add_edge(n2, n3)

    test_set = {n1.id, n3.id}
    print("Is it independent?", ind_set_problem.evaluate(test_set))  # Expect True
