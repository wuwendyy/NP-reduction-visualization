from npvis.reduction.reduction import Reduction
from npvis.problem.independent_set import IndependentSetProblem
from npvis.problem.three_sat import ThreeSATProblem


class ThreeSatToIndependentSetReduction(Reduction):
    """
    Performs a standard 3-SAT → Independent Set reduction.

    - build_graph_from_formula(): Creates one node per (literal-occurrence) in each clause.
      Fully connects each clause's nodes, then connects complementary literal-nodes across clauses.
    - sol1tosol2(): Maps a SAT assignment to an Independent Set.
    - sol2tosol1(): Maps an Independent Set back to a SAT assignment.
    """

    def __init__(self, three_sat_problem: ThreeSATProblem, ind_set_problem: IndependentSetProblem):
        super().__init__(three_sat_problem, ind_set_problem)
        self.input1_to_input2_pairs = {}  # literal_reference -> node_reference
        self.input2_to_input1_pairs = {}  # node_reference -> literal_reference
        self.output1_to_output2_pairs = {}
        self.output2_to_output1_pairs = {}
        
        
    def build_graph_from_formula(self):
        formula_list = self.problem1.clauses

        # # You can do something like:
        # print("DEBUG: formula_list =", formula_list)
        # print("DEBUG: formula_list types =", [(type(item), item) for item in formula_list])

        # for clause in formula_list:
        #     print("DEBUG: Clause type =", type(clause), "Clause value =", clause)
        #     for literal in clause.variables:
        #         print("DEBUG: Literal type =", type(literal), "Literal value =", literal)
                
        # Create nodes per clause and fully connect them.
        for clause in formula_list:
            clause_nodes = []
            for literal in clause.variables:
                # key = (var_id, is_not_negated, c_idx)
                # name = f"x{var_id}" if is_not_negated else f"¬x{var_id}"
                node = self.problem2.add_node(literal.name)
                self.input1_to_input2_pairs[literal] = node
                self.input2_to_input1_pairs[node] = literal
                clause_nodes.append(node)

            self.problem2.add_group(clause_nodes)
            for i in range(len(clause_nodes)):
                for j in range(i + 1, len(clause_nodes)):
                    self.problem2.add_edge(clause_nodes[i], clause_nodes[j])

        # Connect complementary literal occurrences across clauses.
        # graph = self.problem2.get_graph()
        items = list(self.input1_to_input2_pairs.items())
        for i in range(len(items)):
            literal_A, node_A = items[i]
            for j in range(i + 1, len(items)):
                literal_B, node_B = items[j]
                if literal_A.name == literal_B.name and literal_A.is_not_negated != literal_B.is_not_negated:
                    node_B = self.input1_to_input2_pairs[literal_B]
                    self.problem2.add_edge(node_A, node_B)

    def sol1tosol2(self, sat_assignment):
        independent_set = set()
        formula_list = self.problem1.clauses

        for clause in formula_list:
            chosen_node = None
            for literal in clause.variables:
                # Key includes c_idx, so we find the node for this literal occurrence
                # key = (var_id, is_not_negated, c_idx)
                # var_id corresponds to the literal name
                node = self.input1_to_input2_pairs[literal]
                var_id = literal.name
                is_not_negated = literal.is_not_negated
                # If the assignment matches the literal, consider picking it
                if sat_assignment.get(var_id, False) == is_not_negated:
                    chosen_node = node
                    break  # Once we pick a single literal in this clause, we stop

            if chosen_node is not None:
                independent_set.add(chosen_node)
                self.output1_to_output2_pairs[literal] = node

        return independent_set

    # def sol2tosol1(self, independent_set):
    #     assignment = {}
    #     for node in independent_set:
            
    #         self.output2_to_output1_pairs[node] = literal  # Reverse mapping
    #         if node in self.input2_to_input1_pairs:
    #             literal = self.input2_to_input1_pairs[node]
    #             assignment[literal.name] = literal.is_not_negated
    #     return assignment
    
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
        formula_list = self.problem1.clauses  # ✅ Fixing the access to formula

        print(f"Independent Set Input (sorted): {sorted(independent_set)}\n")

        # Assign values based on selected nodes in the independent set
        for literal, node in self.input1_to_input2_pairs.items():
            clause_idx = literal.clause_id
            if node.node_id in independent_set:
                var = literal.name
                is_not_negated = literal.is_not_negated
                clause_id = literal.clause_id
                id = literal.id  # (i, False) → ¬x_i, (i, True) → x_i

                sat_assignment[var] = is_not_negated  # 1 = 1, not 0 = 1

                self.output2_to_output1_pairs[node] = literal  # Reverse mapping

                print(f"  Node {node.node_id} corresponds to Literal {literal} in Clause {clause_idx}")
                print(f"    Assigning Variable x{var} -> {sat_assignment[var]}\n")

        # Ensure all variables in the formula are assigned a value
        # all_vars = {var for clause in formula_list for var, _ in clause}  # ✅ Fix: Using correct formula structure
        all_vars = {literal.name for clause in formula_list for literal in clause.variables}  # ✅ Fix: Using correct formula structure

        for var in sorted(all_vars):
            if var not in sat_assignment:
                for clause in formula_list:  # ✅ Fix: Iterate over structured formula list
                    for literal in clause.variables:
                        
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

        # print(f"Recovered SAT Assignment: {sat_assignment}\n")
        # print("Conversion to SAT Assignment completed!\n")
        return sat_assignment

    def test_solution(self, sat_assignment):
        satisfied = self.problem1.evaluate(sat_assignment)
        chosen = self.sol1tosol2(sat_assignment)
        valid_independent = self.problem2.is_independent_set(chosen)
        return satisfied, valid_independent
