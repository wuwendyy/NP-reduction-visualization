import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Elements.element import Graph, Node, Edge  # Now it should work


class ThreeSatToIndependentSetReduction:
    def __init__(self, formula):
        """
        Initializes the reduction with a given 3-SAT formula.
        
        Args:
            formula: List of clauses, where each clause is a list of literals.
                     Example: [[(1, False), (2, True), (3, False)], ...]
        """
        self.formula = formula
        self.graph, self.clause_vertices, self.literal_to_formula_indices, self.literal_id_to_node_id = self.build_3sat_graph_from_formula()

    def build_3sat_graph_from_formula(self):
        """
        Constructs a 3-SAT graph using custom Graph, Node, and Edge classes.

        Returns:
            G: Custom Graph object.
            clause_vertices: List of lists mapping clause indices to their corresponding node IDs.
            literal_to_formula_indices: A mapping of literals to positions in the formula.
            literal_id_to_node_id: Mapping from (literal, clause_idx) → node_id for faster lookups.
        """
        G = Graph()
        clause_vertices = []
        literal_id_to_node_id = {}
        literal_to_formula_indices = {}
        node_id = 1  # Node index counter

        for c_idx, clause in enumerate(self.formula):
            c_nodes = []
            for lit_idx, literal in enumerate(clause):
                node = Node(node_id, str(literal))  # Create a new Node
                G.add_node(node)
                c_nodes.append(node)

                # Store mappings
                literal_id_to_node_id[(literal, c_idx)] = node
                if literal not in literal_to_formula_indices:
                    literal_to_formula_indices[literal] = []
                literal_to_formula_indices[literal].append((c_idx, lit_idx))

                node_id += 1

            # Ensure the clause forms a triangle (3 literals) or a single edge (2 literals)
            if len(c_nodes) == 3:
                G.add_edge(Edge(c_nodes[0], c_nodes[1]))
                G.add_edge(Edge(c_nodes[1], c_nodes[2]))
                G.add_edge(Edge(c_nodes[2], c_nodes[0]))
            elif len(c_nodes) == 2:
                G.add_edge(Edge(c_nodes[0], c_nodes[1]))

            clause_vertices.append(c_nodes)

        # Add edges between complementary literals (x and ¬x) across clauses
        for c_idx in range(len(self.formula) - 1):  # Check neighboring clauses
            for literal in self.formula[c_idx]:
                opposite_literal = (literal[0], not literal[1])  # Flip negation
                if opposite_literal in self.formula[c_idx + 1]:
                    node1 = literal_id_to_node_id.get((literal, c_idx))
                    node2 = literal_id_to_node_id.get((opposite_literal, c_idx + 1))
                    if node1 is not None and node2 is not None:
                        G.add_edge(Edge(node1, node2))

        return G, clause_vertices, literal_to_formula_indices, literal_id_to_node_id

    def sol1tosol2(self, sat_assignment):
        """
        Convert a satisfying assignment of 3-SAT into an Independent Set solution.

        Args:
            sat_assignment: Dictionary mapping variables to their truth values (True/False).

        Returns:
            A set of selected nodes forming an independent set.
        """
        print("\nConverting SAT assignment to Independent Set...\n")
        independent_set = set()

        print(f"SAT Assignment: {sat_assignment}\n")

        for c_idx, clause in enumerate(self.formula):
            for literal in clause:
                var, is_not_negated = literal  # (i, False) → ¬x_i, (i, True) → x_i

                if (sat_assignment[var] == 1 and is_not_negated) or (sat_assignment[var] == 0 and not is_not_negated):
                    node = self.literal_id_to_node_id.get((literal, c_idx))
                    if node:
                        independent_set.add(node.node_id)
                        print(f"  Node {node.node_id} (Literal {literal} in Clause {c_idx}) added to Independent Set")

        print(f"\nIndependent Set Solution: {sorted(independent_set)}\n")
        print("Conversion to Independent Set completed!\n")
        return independent_set

    def sol2tosol1(self, independent_set):
        """
        Convert an Independent Set solution back into a satisfying assignment for 3-SAT.

        Args:
            independent_set: Set of selected nodes forming an independent set.

        Returns:
            A dictionary mapping variables to their correct True/False values.
        """
        print("\nConverting Independent Set back to SAT assignment...\n")
        sat_assignment = {}

        print(f"Independent Set Input (sorted): {sorted(independent_set)}\n")

        for (literal, clause_idx), node in self.literal_id_to_node_id.items():
            if node.node_id in independent_set:
                var, is_not_negated = literal
                sat_assignment[var] = is_not_negated
                print(f"  Node {node.node_id} corresponds to Literal {literal} in Clause {clause_idx}")
                print(f"    Assigning Variable x{var} -> {sat_assignment[var]}\n")

        all_vars = {var for clause in self.formula for var, _ in clause}
        for var in sorted(all_vars):
            if var not in sat_assignment:
                for clause in self.formula:
                    for literal in clause:
                        lit_var, is_not_negated = literal
                        if lit_var == var:
                            sat_assignment[var] = not is_not_negated
                            print(f"  Variable x{var} missing from independent set. Found literal {literal}. Assigning x{var} -> {sat_assignment[var]}\n")
                            break
                    if var in sat_assignment:
                        break

        print(f"Recovered SAT Assignment: {sat_assignment}\n")
        print("Conversion to SAT Assignment completed!\n")
        return sat_assignment

    def is_independent_set(self, node_set):
        """
        Checks if the given set of node_ids forms an independent set.

        Args:
            node_set: set of node IDs to check.

        Returns:
            bool: True if it is an independent set, False otherwise.
        """
        node_set = set(node_set)

        for node1_id in node_set:
            for node2_id in node_set:
                if node1_id != node2_id and self.graph.hasEdge(self.graph.get_node_by_id(node1_id), self.graph.get_node_by_id(node2_id)):
                    return False  # Found an edge within the set
        return True
