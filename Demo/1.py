import sys
from element import Graph, Formula
from helpers import Node, Edge
import itertools

class ThreeSatToIndependentSetReduction:
    def __init__(self, formula):
        """
        Initialize the reduction from 3-SAT to Independent Set.
        Args:
            formula: Formula object containing clauses and variables.
        """
        self.formula = formula
        self.formula.variables = self._extract_variables()
        self.graph = Graph()
        self.node_mapping = {}  # Maps (clause_idx, literal_idx) -> Node object
        self._build_graph()

    def _extract_variables(self):
        """
        Extract unique variables from the formula clauses.
        """
        variables = set()
        for clause in self.formula.clauses:
            for literal in clause:
                variables.add(literal[0])
        return variables

    def _build_graph(self):
        """
        Construct the Independent Set graph from the 3-SAT formula.
        """
        node_id = 0
        for c_idx, clause in enumerate(self.formula.clauses):
            clause_nodes = []
            for lit_idx, literal in enumerate(clause):
                node = Node(node_id, name=f"{literal}")
                self.graph.add_node(node)
                self.node_mapping[(c_idx, lit_idx)] = node
                clause_nodes.append(node)
                node_id += 1
            
            # Create edges within each clause (ensuring at most one can be picked in an independent set)
            for u, v in itertools.combinations(clause_nodes, 2):
                edge = Edge(u, v)
                self.graph.add_edge(edge)
        
        # Add conflict edges between literals and their negations
        for node1 in self.graph.nodes:
            lit1 = eval(node1.name)
            negated_lit = (lit1[0], not lit1[1])  # Flip negation
            
            for node2 in self.graph.nodes:
                if eval(node2.name) == negated_lit and node1 != node2:
                    edge = Edge(node1, node2)
                    self.graph.add_edge(edge)

    def in1toin2(self):
        """
        Converts the 3-SAT problem into an Independent Set problem by constructing the graph.
        """
        return self.graph
    
    def sol1tosol2(self, sat_assignment):
        """
        Convert a satisfying assignment of 3-SAT into an Independent Set solution.
        Args:
            sat_assignment: Dictionary mapping variables to True/False values.
        Returns:
            A set of selected nodes forming an independent set.
        """
        independent_set = set()
        for (c_idx, lit_idx), node in self.node_mapping.items():
            var, is_negated = eval(node.name)
            if sat_assignment[var] != is_negated:  # If literal is True in assignment
                independent_set.add(node)
        return independent_set
    
    def sol2tosol1(self, independent_set):
        """
        Convert an Independent Set solution back into a satisfying assignment for 3-SAT.
        Args:
            independent_set: Set of selected nodes forming an independent set.
        Returns:
            A dictionary mapping variables to True/False values.
        """
        assignment = {var: False for var in self.formula.variables}
        for node in independent_set:
            var, is_negated = eval(node.name)
            assignment[var] = not is_negated
        return assignment
    
    def display(self):
        """
        Displays the Independent Set graph.
        """
        self.graph.display()

# Example usage
if __name__ == "__main__":
    formula = Formula()
    formula.clauses = [
        [(1, False), (2, True), (3, False)],
        [(2, False), (3, True), (4, False)],
        [(1, False), (2, True), (4, False)]
    ]
    formula.variables = {1, 2, 3, 4}
    
    reduction = ThreeSatToIndependentSetReduction(formula)
    reduction.display()
    
    # Example SAT assignment: {1: True, 2: False, 3: True, 4: False}
    sat_assignment = {1: True, 2: False, 3: True, 4: False}
    independent_set = reduction.sol1tosol2(sat_assignment)
    print("Independent Set Solution:", [node.node_id for node in independent_set])
    
    # Convert back to SAT assignment
    reconstructed_assignment = reduction.sol2tosol1(independent_set)
    print("Reconstructed SAT Assignment:", reconstructed_assignment)
