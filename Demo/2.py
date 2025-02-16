import networkx as nx
import itertools
from elements import Formula
from helpers import Node, Edge
from elements import Graph, Formula
from helpers import Node, Edge
from three_sat_reduction import ThreeSatToIndependentSetReduction
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
        self.node_mapping = {}  # Maps (clause_idx, literal_idx) -> node_id
        self.assignment_mapping = {}  # Maps (variable, is_negated, clause_idx) -> node_id
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
                node_label = f"{literal} (Clause {c_idx})"
                self.graph.add_node(node_id, literal=literal, label=node_label, clause_index=c_idx)
                self.node_mapping[(c_idx, lit_idx)] = node_id
                clause_nodes.append(node_id)

                # Store clause-specific variable-to-node mapping
                var, is_negated = literal
                if (var, is_negated, c_idx) not in self.assignment_mapping:
                    self.assignment_mapping[(var, is_negated, c_idx)] = node_id

                node_id += 1
            
            # Create edges within each clause (ensuring at most one can be picked in an independent set)
            for u, v in itertools.combinations(clause_nodes, 2):
                self.graph.add_edge(u, v)
        
        # Add conflict edges between literals and their negations
        seen_vars = {}
        for (var, is_negated, c_idx), node_id in self.assignment_mapping.items():
            if (var, is_negated) not in seen_vars:
                seen_vars[(var, is_negated)] = []
            seen_vars[(var, is_negated)].append(node_id)
        
        for var in self.formula.variables:
            pos_nodes = seen_vars.get((var, True), [])
            neg_nodes = seen_vars.get((var, False), [])
            for u in pos_nodes:
                for v in neg_nodes:
                    self.graph.add_edge(u, v)

    def build_3sat_graph_from_formula(self):
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

                if (literal, c_idx) not in literal_to_formula_indices:
                    literal_to_formula_indices[(literal, c_idx)] = []
                literal_to_formula_indices[(literal, c_idx)].append((c_idx, lit_idx))

            clause_vertices.append(clause_nodes)

        return G, clause_vertices, self.formula.clauses, literal_to_formula_indices

    def sol1tosol2(self, sat_assignment):
        """
        Convert a satisfying assignment of 3-SAT into an Independent Set solution.
        Args:
            sat_assignment: Dictionary mapping variables to True/False values.
        Returns:
            A set of selected nodes forming an independent set.
        """
        independent_set = set()
        for (var, value, c_idx), node_id in self.assignment_mapping.items():
            if var in sat_assignment and sat_assignment[var] == value:
                independent_set.add(node_id)
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
        for (var, value, c_idx), node_id in self.assignment_mapping.items():
            if node_id in independent_set:
                assignment[var] = value
        return assignment
