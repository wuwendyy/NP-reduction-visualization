import networkx as nx
import itertools
from element import Formula
from helpers import Node, Edge
import pygame
import networkx as nx
import math
from three_sat_visualizer import ThreeSatGraphVisualizer



class ThreeSatToIndependentSetReduction:
    def __init__(self, formula):
        """
        Initialize the reduction from 3-SAT to Independent Set.
        Args:
            formula: Formula object containing clauses and variables.
        """
        self.formula = formula
        self.formula.variables = self._extract_variables()
        self.graph = nx.Graph()
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
                node_label = f"{literal}"  # Label as (var, neg)
                self.graph.add_node(node_id, literal=literal, label=node_label)
                self.node_mapping[(c_idx, lit_idx)] = node_id
                clause_nodes.append(node_id)
                node_id += 1
            
            # Create edges within each clause (ensuring at most one can be picked in an independent set)
            for u, v in itertools.combinations(clause_nodes, 2):
                self.graph.add_edge(u, v)
        
        # Add conflict edges between literals and their negations
        for node1 in self.graph.nodes():
            lit1 = self.graph.nodes[node1]["literal"]
            negated_lit = (lit1[0], not lit1[1])  # Flip negation
            
            for node2 in self.graph.nodes():
                if self.graph.nodes[node2]["literal"] == negated_lit and node1 != node2:
                    self.graph.add_edge(node1, node2)

    def build_3sat_graph(self):
        """
        Constructs the 3-SAT graph for visualization.
        Returns:
            G: NetworkX graph representing the problem.
            clause_vertices: List of lists mapping clause indices to their corresponding node IDs.
            formula: The original 3-SAT formula.
            literal_to_formula_indices: A mapping of literals to positions in the formula.
        """
        G = self.graph
        clause_vertices = []
        literal_to_formula_indices = {}

        for c_idx, clause in enumerate(self.formula.clauses):
            clause_nodes = []
            for lit_idx, literal in enumerate(clause):
                node_id = self.node_mapping[(c_idx, lit_idx)]
                clause_nodes.append(node_id)

                if literal not in literal_to_formula_indices:
                    literal_to_formula_indices[literal] = []
                literal_to_formula_indices[literal].append((c_idx, lit_idx))

            clause_vertices.append(clause_nodes)

        return G, clause_vertices, self.formula.clauses, literal_to_formula_indices

# Example Formula
formula = Formula()
formula.clauses = [
    [(1, False), (2, True), (3, False)],
    [(2, False), (3, True), (4, False)],
    [(1, False), (2, True), (4, False)]
]

# Create Reduction Object
reduction = ThreeSatToIndependentSetReduction(formula)

# Generate Graph for Visualization
G, clause_vertices, formula, literal_to_formula_indices = reduction.build_3sat_graph()

# Visualize
visualizer = ThreeSatGraphVisualizer(
    graph=G,
    clause_vertices=clause_vertices,
    formula=formula,
    literal_to_formula_indices=literal_to_formula_indices
)

visualizer.run()
