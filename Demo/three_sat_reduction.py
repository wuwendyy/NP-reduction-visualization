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
    #             var, is_not_negated = literal
    #             sat_assignment[var] = not is_not_negated
    #             print(f"  Node {node_id} corresponds to Literal {literal} in Clause {clause_idx}")
    #             print(f"    Assigning Variable x{var} -> {'True' if not is_not_negated else 'False'}\n")

    #     print(f"Recovered SAT Assignment: {sat_assignment}\n")
    #     print("Conversion to SAT Assignment completed!\n")
    #     return sat_assignment

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

        # Iterate through each clause to find literals that evaluate to 1
        for c_idx, clause in enumerate(self.formula):
            for literal in clause:
                var, is_not_negated = literal  # (i, False) → ¬x_i, (i, True) → x_i

                # Determine if the literal should be added based on its truth value
                if (sat_assignment[var] == 1 and is_not_negated == True) or (sat_assignment[var] == 0 and is_not_negated == False):
                    lit_value = 1  # This literal is true based on the assignment
                else:
                    lit_value = 0  # This literal is false

                if lit_value == 1:  # Select literals that evaluate to 1
                    node_id = self.literal_id_to_node_id.get((literal, c_idx))
                    if node_id is not None:
                        independent_set.add(node_id)
                        print(f"  Node {node_id} (Literal {literal} in Clause {c_idx}) added to Independent Set")

        print(f"\nIndependent Set Solution: {sorted(independent_set)}\n")
        print("Conversion to Independent Set completed!\n")
        return independent_set


    # def sol2tosol1(self, independent_set):
    #     """
    #     Convert an Independent Set solution back into a satisfying assignment for 3-SAT.
        
    #     Args:
    #         independent_set: Set of selected nodes forming an independent set.

    #     Returns:
    #         A dictionary mapping variables to their correct True/False values.
    #     """
    #     print("\nConverting Independent Set back to SAT assignment...\n")
    #     sat_assignment = {}

    #     print(f"Independent Set Input (sorted): {sorted(independent_set)}\n")

    #     # Step 1: Assign truth values based on independent set nodes
    #     for (literal, clause_idx), node_id in self.literal_id_to_node_id.items():
    #         if node_id in independent_set:
    #             var, is_not_negated = literal  # (x_var, True) → x_var ; (x_var, False) → ¬x_var

    #             # If is_not_negated is True → x_var = True
    #             # If is_not_negated is False → ¬x_var is in the independent set, so x_var = False
    #             assigned_value = True if is_not_negated else False

    #             # Only assign if not already assigned
    #             if var not in sat_assignment:
    #                 sat_assignment[var] = assigned_value
    #                 print(f"  Node {node_id} corresponds to Literal {literal} in Clause {clause_idx}")
    #                 print(f"    Assigning Variable x{var} -> {sat_assignment[var]}\n")

    #     # Step 2: Ensure all variables have an assignment (default to False if missing)
    #     all_vars = {var for clause in self.formula for var, _ in clause}
    #     for var in sorted(all_vars):  # Sorting for consistent output
    #         if var not in sat_assignment:
    #             sat_assignment[var] = False  # Default missing variables to False
    #             print(f"  WARNING: Variable x{var} missing from independent set. Defaulting to False.\n")

    #     # Step 3: Print the final recovered assignment in the expected sequence
    #     expected_order = [1, 2, 3, 4]  # Define the expected sequence
    #     ordered_assignment = {k: sat_assignment[k] for k in expected_order}

    #     print(f"Recovered SAT Assignment (ordered): {ordered_assignment}\n")
    #     print("Conversion to SAT Assignment completed!\n")
    #     return ordered_assignment

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

        # Step 1: Assign truth values based on independent set nodes
        for (literal, clause_idx), node_id in self.literal_id_to_node_id.items():
            if node_id in independent_set:
                var, is_not_negated = literal  # (x_var, True) → x_var ; (x_var, False) → ¬x_var

                # If is_not_negated is True → x_var = True
                # If is_not_negated is False → ¬x_var is in the independent set, so x_var = False
                assigned_value = True if is_not_negated else False

                # Only assign if not already assigned
                if var not in sat_assignment:
                    sat_assignment[var] = assigned_value
                    print(f"  Node {node_id} corresponds to Literal {literal} in Clause {clause_idx}")
                    print(f"    Assigning Variable x{var} -> {sat_assignment[var]}\n")

        # Step 2: Assign missing variables based on their literals in the formula
        all_vars = {var for clause in self.formula for var, _ in clause}
        for var in sorted(all_vars):  # Sorting for consistent output
            if var not in sat_assignment:
                # Find any occurrence of the variable in the formula
                for clause in self.formula:
                    for literal in clause:
                        lit_var, is_not_negated = literal
                        if lit_var == var:
                            # If literal is negated (¬x_var), assign x_var = True
                            # If literal is not negated (x_var), assign x_var = False
                            sat_assignment[var] = not is_not_negated
                            print(f"  Variable x{var} missing from independent set. Found literal {literal}. Assigning x{var} -> {sat_assignment[var]}\n")
                            break  # Found a valid assignment, exit loop
                    if var in sat_assignment:
                        break  # Exit outer loop once assigned

        # Step 3: Print the final recovered assignment in the expected sequence
        expected_order = [1, 2, 3, 4]  # Define the expected sequence
        ordered_assignment = {k: sat_assignment[k] for k in expected_order}

        print(f"Recovered SAT Assignment (ordered): {ordered_assignment}\n")
        print("Conversion to SAT Assignment completed!\n")
        return ordered_assignment
