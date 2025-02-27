import networkx as nx

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
        Constructs a 3-SAT graph for visualization.

        Returns:
            G: NetworkX graph representing the problem.
            clause_vertices: List of lists mapping clause indices to their corresponding node IDs.
            literal_to_formula_indices: A mapping of literals to positions in the formula.
            literal_id_to_node_id: Mapping from (literal, clause_idx) → node_id for faster lookups.
        """
        G = nx.Graph()
        clause_vertices = []
        literal_id_to_node_id = {}
        literal_to_formula_indices = {}
        node_id = 1  # Node index counter

        for c_idx, clause in enumerate(self.formula):
            c_nodes = []
            for lit_idx, literal in enumerate(clause):
                G.add_node(node_id, literal=literal, clause_index=c_idx)
                c_nodes.append(node_id)
                
                # Store mappings
                literal_id_to_node_id[(literal, c_idx)] = node_id
                if literal not in literal_to_formula_indices:
                    literal_to_formula_indices[literal] = []
                literal_to_formula_indices[literal].append((c_idx, lit_idx))

                node_id += 1

            # Ensure the clause forms a triangle (3 literals) or a single edge (2 literals)
            if len(c_nodes) == 3:
                G.add_edges_from([(c_nodes[0], c_nodes[1]), (c_nodes[1], c_nodes[2]), (c_nodes[2], c_nodes[0])])
            elif len(c_nodes) == 2:
                G.add_edge(c_nodes[0], c_nodes[1])

            clause_vertices.append(c_nodes)

        # Add edges between complementary literals (x and ¬x) across clauses
        for c_idx in range(len(self.formula) - 1):  # Check neighboring clauses
            for literal in self.formula[c_idx]:
                opposite_literal = (literal[0], not literal[1])  # Flip negation
                if opposite_literal in self.formula[c_idx + 1]:
                    node1 = literal_id_to_node_id.get((literal, c_idx))
                    node2 = literal_id_to_node_id.get((opposite_literal, c_idx + 1))
                    if node1 is not None and node2 is not None and not G.has_edge(node1, node2):
                        G.add_edge(node1, node2)

        return G, clause_vertices, literal_to_formula_indices, literal_id_to_node_id

    # def sol1tosol2(self, sat_assignment):
    #     """
    #     Convert a satisfying assignment of 3-SAT into an Independent Set solution.
        
    #     Args:
    #         sat_assignment: Dictionary mapping variables to their truth values (0/1).

    #     Returns:
    #         A set of selected literals (tuples) forming an independent set.
    #     """
    #     print("\nConverting SAT assignment to Independent Set...\n")
    #     independent_set = set()
        
    #     print(f"SAT Assignment: {sat_assignment}\n")

    #     for var, value in sat_assignment.items():
    #         lit = (var, value)  # Selects x if True, ¬x if False
    #         print(f"  Processing Variable x{var} -> Assigned {value} -> Selecting Literal {lit}")

    #         found = False
    #         for c_idx in range(len(self.formula)):
    #             if lit in self.formula[c_idx]:
    #                 node_id = self.literal_id_to_node_id.get((lit, c_idx))
    #                 if node_id is not None:
    #                     independent_set.add(node_id)
    #                     print(f"    Found in Clause {c_idx}: Node {node_id} added to Independent Set")
    #                     found = True
            
    #         if not found:
    #             print(f"    WARNING: Literal {lit} not found in any clause!")

    #     print(f"\nIndependent Set Solution: {independent_set}\n")
    #     print("Conversion to Independent Set completed!\n")
    #     return independent_set

    # def sol2tosol1(self, independent_set):
    #     """
    #     Convert an Independent Set solution back into a satisfying assignment for 3-SAT.
        
    #     Args:
    #         independent_set: Set of selected nodes forming an independent set.

    #     Returns:
    #         A dictionary mapping variables to True/False values.
    #     """
    #     print("\nConverting Independent Set back to SAT assignment...\n")
    #     sat_assignment = {}

    #     print(f"Independent Set Input: {independent_set}\n")

    #     for (literal, clause_idx), node_id in self.literal_id_to_node_id.items():
    #         if node_id in independent_set:
    #             var, is_negated = literal
    #             sat_assignment[var] = not is_negated
    #             print(f"  Node {node_id} corresponds to Literal {literal} in Clause {clause_idx}")
    #             print(f"    Assigning Variable x{var} -> {'True' if not is_negated else 'False'}\n")

    #     print(f"Recovered SAT Assignment: {sat_assignment}\n")
    #     print("Conversion to SAT Assignment completed!\n")
    #     return sat_assignment
