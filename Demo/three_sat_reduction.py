import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Elements.element import * 
from Elements.helpers import * 


class ThreeSatToIndependentSetReduction:
    def __init__(self, formula: Formula):
        """
        Initializes the reduction with a given 3-SAT formula.
        
        Args:
            formula: List of clauses, where each clause is a list of literals.
                     Example: [[(1, False), (2, True), (3, False)], ...]
        """
        self.formula = formula
        # literal id to node id = input to input pair
        self.graph, self.clause_vertices, self.literal_to_formula_indices, self.lit_to_node_id, self.literal_id_to_node_id = self.build_3sat_graph_from_formula()
        self.output1_to_output2 = {} 
        self.output2_to_output1 = {}
        
    
    def add_edges_for_clause(self, G, nodes):
        """Ensure the clause forms a triangle (3 literals) or a single edge (2 literals)."""
        if len(nodes) == 3:
            G.add_edge(Edge(nodes[0], nodes[1]))
            G.add_edge(Edge(nodes[1], nodes[2]))
            G.add_edge(Edge(nodes[2], nodes[0]))
        elif len(nodes) == 2:
            G.add_edge(Edge(nodes[0], nodes[1]))
        
    # def build_3sat_graph_from_formula(self):
    #     """
    #     Constructs a 3-SAT graph using custom Graph, Node, and Edge classes.

    #     Returns:
    #         G: Custom Graph object.
    #         clause_vertices: List of lists mapping clause indices to their corresponding node IDs.
    #         literal_to_formula_indices: A mapping of literals to positions in the formula.
    #         lit_to_node_id: Mapping from (literal, clause_idx) → node_id for faster lookups.
    #     """
    #     G = Graph()
    #     clause_vertices = []
    #     lit_to_node_id = {}
    #     literal_to_formula_indices = {}
    #     literal_id_to_node_id = {}
    #     node_id = 1  # Node index counter

    #     formula_list = self.formula.get_as_list() 
        
    #     for c_idx, clause in enumerate(formula_list):
    #         c_nodes = []

    #         for lit_idx, literal in enumerate(clause):
    #             print (literal)
    #             print(lit_idx)
    #             node = Node(node_id, str(literal))  # Create a new Node
    #             G.add_node(node)
    #             c_nodes.append(node)

    #             # Store mappings
    #             lit_to_node_id[(literal, c_idx)] = node  # Maps (literal, clause index) to Node object
    #             literal_to_formula_indices.setdefault(literal, []).append((c_idx, lit_idx))
    #             print(f"Literal ID: {literal.id} → Node ID: {node_id}")
    #             literal_id_to_node_id[literal.id] = node_id  # Store only literal_id -> node_id mapping

    #             node_id += 1  # Increment node ID

    #         # Add edges within the clause
    #         self.add_edges_for_clause(G, c_nodes)

    #         clause_vertices.append(c_nodes)

    #     # Add edges between complementary literals (x and ¬x) across clauses
    #     num_clauses = len(formula_list)

    #     for c_idx in range(num_clauses - 1):  # Check neighboring clauses
    #         current_clause = formula_list[c_idx]
    #         next_clause = formula_list[c_idx + 1]

    #         for literal in current_clause:
    #             opposite_literal = (literal.name, not literal.is_not_negated)  # Flip negation
    #             if opposite_literal in next_clause:
    #                 node1 = lit_to_node_id.get((literal, c_idx))
    #                 node2 = lit_to_node_id.get((opposite_literal, c_idx + 1))
    #                 if node1 and node2:
    #                     G.add_edge(Edge(node1, node2))

    #     return G, clause_vertices, literal_to_formula_indices, lit_to_node_id, literal_id_to_node_id
    
    def build_3sat_graph_from_formula(self):
        """
        Constructs a 3-SAT graph using the custom Graph, Node, and Edge classes.

        Returns:
            G: Custom Graph object.
            clause_vertices: List of lists mapping clause indices to their corresponding node objects.
            literal_to_formula_indices: A mapping of literals to positions in the formula.
            lit_to_node_id: Mapping from (literal, clause_idx) → node object for fast lookups.
            literal_id_to_node_id: Mapping from literal_id → node_id for efficient retrieval.
        """
        G = Graph()
        clause_vertices = []
        lit_to_node_id = {}
        literal_to_formula_indices = {}
        literal_id_to_node_id = {}
        node_id = 1  # Node index counter

        formula_list = self.formula.get_as_list()

        # Step 1: Create Nodes and Groups
        for c_idx, clause in enumerate(formula_list):
            c_nodes = []

            for lit_idx, literal in enumerate(clause):
                node = Node(node_id, str(literal))  # Create Node with unique ID and name
                G.add_node(node)
                c_nodes.append(node)

                # Store mappings
                lit_to_node_id[(literal, c_idx)] = node
                literal_to_formula_indices.setdefault(literal, []).append((c_idx, lit_idx))
                literal_id_to_node_id[literal.id] = node_id

                print(f"Literal ID: {literal.id} → Node ID: {node_id}")  # Debug output
                node_id += 1

            # Store clause as a group of three nodes
            clause_vertices.append(c_nodes)
            G.groups.append(c_nodes)

            # Step 2: Add edges between nodes within the clause (fully connected)
            for i in range(len(c_nodes)):
                for j in range(i + 1, len(c_nodes)):
                    G.add_edge(Edge(c_nodes[i], c_nodes[j]))

        # Step 3: Add edges between complementary literals (x and ¬x) across clauses
        for c_idx in range(len(formula_list) - 1):
            for literal in formula_list[c_idx]:
                opposite_literal = next(
                    (lit for lit in formula_list[c_idx + 1] if lit.name == literal.name and lit.is_not_negated != literal.is_not_negated),
                    None
                )
                if opposite_literal:
                    node1 = lit_to_node_id.get((literal, c_idx))
                    node2 = lit_to_node_id.get((opposite_literal, c_idx + 1))
                    if node1 and node2:
                        G.add_edge(Edge(node1, node2))

        return G, clause_vertices, literal_to_formula_indices, lit_to_node_id, literal_id_to_node_id

    # def sol1tosol2(self, sat_assignment):
    
    def sol1tosol2(self, sat_assignment):
        """
        Convert a satisfying assignment of 3-SAT into an Independent Set solution.

        Args:
            sat_assignment: Dictionary mapping variables to their truth values (1/0).

        Returns:
            A set of selected nodes forming an independent set.
        """
        print("\nConverting SAT assignment to Independent Set...\n")
        independent_set = set()

        # Ensure we get the structured formula list
        formula_list = self.formula.get_as_list()

        print(f"SAT Assignment: {sat_assignment}\n")

        for c_idx, clause in enumerate(formula_list):  # Use the correct formula list
            for literal in clause:
                var = literal.name
                is_not_negated = literal.is_not_negated
                clause_id = literal.clause_id
                id = literal.id  # (i, False) → ¬x_i, (i, True) → x_i

                # Check if the assignment satisfies the literal
                if (sat_assignment[var] == 1 and is_not_negated) or (sat_assignment[var] == 0 and not is_not_negated):
                    node = self.lit_to_node_id.get((literal, c_idx))  # Correct lookup
                    if node:
                        independent_set.add(node.node_id)
                        self.output1_to_output2[literal] = node
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

        # Fetch structured formula list
        formula_list = self.formula.get_as_list()  # ✅ Fixing the access to formula

        print(f"Independent Set Input (sorted): {sorted(independent_set)}\n")

        # Assign values based on selected nodes in the independent set
        for (literal, clause_idx), node in self.lit_to_node_id.items():
            if node.node_id in independent_set:
                var = literal.name
                is_not_negated = literal.is_not_negated
                clause_id = literal.clause_id
                id = literal.id  # (i, False) → ¬x_i, (i, True) → x_i

                sat_assignment[var] = is_not_negated  # 1 = 1, not 0 = 1

                self.output2_to_output1[node] = literal  # Reverse mapping

                print(f"  Node {node.node_id} corresponds to Literal {literal} in Clause {clause_idx}")
                print(f"    Assigning Variable x{var} -> {sat_assignment[var]}\n")

        # Ensure all variables in the formula are assigned a value
        # all_vars = {var for clause in formula_list for var, _ in clause}  # ✅ Fix: Using correct formula structure
        all_vars = {literal.name for clause in formula_list for literal in clause}

        for var in sorted(all_vars):
            if var not in sat_assignment:
                for clause in formula_list:  # ✅ Fix: Iterate over structured formula list
                    for literal in clause:
                        
                        lit_var = literal.name
                        is_not_negated = literal.is_not_negated
                        clause_id = literal.clause_id
                        id = literal.id  # (i, False) → ¬x_i, (i, True) → x_i

                        if lit_var == var:
                            sat_assignment[var] = not is_not_negated  # Assign based on literal negation
                            print(f"  Variable x{var} missing from independent set. Found literal {literal}. Assigning x{var} -> {sat_assignment[var]}\n")
                            break
                    if var in sat_assignment:
                        break  # Stop searching once assigned

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
