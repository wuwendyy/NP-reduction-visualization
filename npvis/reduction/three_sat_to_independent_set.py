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

    def __init__(self, three_sat_problem: ThreeSATProblem, ind_set_problem: IndependentSetProblem, debug=False):
        super().__init__(three_sat_problem, ind_set_problem)
        self.input1_to_input2_pairs = {}  # literal_reference -> node_reference
        self.input2_to_input1_pairs = {}  # node_reference -> literal_reference
        self.output1_to_output2_pairs = {}
        self.output2_to_output1_pairs = {}

        # Enable or disable debug prints
        self.DEBUG = debug

    def _debug_print(self, msg: str):
        """Helper function to print debug messages if self.DEBUG is True."""
        if self.DEBUG:
            print("[DEBUG]", msg)

    def build_graph_from_formula(self):
        self._debug_print("Starting build_graph_from_formula...")

        formula_list = self.problem1.element.clauses
        self._debug_print(f"Retrieved formula_list with {len(formula_list)} clause(s).")

        # Create nodes per clause and fully connect them.
        for c_idx, clause in enumerate(formula_list, start=1):
            self._debug_print(f"Processing Clause #{c_idx} with {len(clause.variables)} variable(s).")
            clause_nodes = []
            clause_fs = set()  

            for literal in clause.variables:
                clause_fs.add(literal)
                # Create a node for each literal occurrence
                node = self.problem2.add_node(repr(literal))
                self.input1_to_input2_pairs[literal] = node
                self.input2_to_input1_pairs[node] = literal
                clause_nodes.append(node)

                # nodes_fs = frozenset({node})
                # literal_fs = frozenset({literal})
                # self.input1_to_input2_dict[literal_fs] = nodes_fs // temp disabel
                self.add_input1_to_input2_by_pair(literal, node) # just use this
                # self.input2_to_input1_dict[nodes_fs] = literal_fs

                self._debug_print(f"  -- Added literal/node pair [{literal} : {node}] to inp1_to_inp2_dict")
                self._debug_print(f"  Created node '{node.id}' of type '{node.name}' for literal {literal}.")

            # Group the clause's nodes
            self.problem2.add_group(clause_nodes)

            self._debug_print(f"  Added group for Clause #{c_idx}: node IDs {[n.id for n in clause_nodes]}.")

            # add to internal dict (3 literals) : (3 nodes in IS graph)
            # allows check that click all 3 literals will highlight 3 nodes in a triangle and vice versa
            # self.input1_to_input2_dict[frozenset(clause_fs)] = frozenset(clause_nodes)// temp disabel
            # self.input2_to_input1_dict[frozenset(clause_nodes)] = frozenset(clause_fs)
            self._debug_print(f"  -- Added clause/triangle pair [{clause_fs} : {clause_nodes}] to inp1_to_inp2_dict")

            # Fully connect them
            for i in range(len(clause_nodes)):
                for j in range(i + 1, len(clause_nodes)):
                    self.problem2.add_edge(clause_nodes[i], clause_nodes[j])
            self._debug_print(f"  Fully connected the nodes within Clause #{c_idx}.")

        name_literal_dict = {}
        name_node_dict = {}

        # Connect complementary literal occurrences across clauses.
        self._debug_print("Connecting complementary literal occurrences across clauses.")
        items = list(self.input1_to_input2_pairs.items())
        for i in range(len(items)):
            literal_A, node_A = items[i]

            # for appending to input1_to_input2_dict later
            name = literal_A.name
            if literal_A.is_negated:
                name = str(literal_A.name) + "_neg"
                
            if name in name_literal_dict:
                name_literal_dict[name].add(literal_A)
                name_node_dict[name].add(node_A)
            else:
                name_literal_dict[name] = {literal_A}
                name_node_dict[name] = {node_A}
            
            for j in range(i + 1, len(items)):
                literal_B, node_B = items[j]
                # If same var name but opposite negation, connect the nodes
                if literal_A.name == literal_B.name and literal_A.is_negated != literal_B.is_negated:
                    self.problem2.add_edge(node_A, node_B)
                    self._debug_print(
                        f"  Connected complementary literals '{literal_A}' <--> '{literal_B}' "
                        f"via nodes {node_A.id} and {node_B.id}."
                    )

        # finally append
        for name, literals in name_literal_dict.items():
            # self.input1_to_input2_dict[frozenset(literals)] = name_node_dict[name]
            self._debug_print(f"  -- Added same_name_literals/same_name_nodes pair [{literals} : {name_node_dict[name]}] to inp1_to_inp2_dict")
        
        self._debug_print("Finished build_graph_from_formula.\n")

    def solution1_to_solution2(self, sat_assignment):
        """
        Convert a SAT assignment (dict var->bool) to an Independent Set.
        """
        self._debug_print("Starting sol1tosol2 (SAT -> IS) conversion...")
        independent_set = set()
        formula_list = self.problem1.element.clauses

        for clause_idx, clause in enumerate(formula_list, start=1):
            chosen_node = None
            self._debug_print(f"  Evaluating Clause #{clause_idx}...")

            for literal in clause.variables:
                # literal_set.add(literal)
                node = self.input1_to_input2_pairs[literal]
                var_id = literal.name  # The variable name/ID
                is_negated = literal.is_negated
                # for 1:TRUE, get TRUE when using 1 as key
                assigned_value = sat_assignment[int(var_id)]

                self._debug_print(
                    f"    Checking literal {literal} in Clause #{clause_idx}: "
                    f"assignment[var={var_id}]={assigned_value}, "
                    f"is_negated={is_negated}"
                )

                # If assignment matches the literal, add this node to the set
                if assigned_value != is_negated:
                    chosen_node = node
                    self.output1_to_output2_pairs[literal] = node
                    self._debug_print(
                        f"    --> Literal {literal} is satisfied by assignment; picking node {node.id}.")
                    break

            if chosen_node:
                independent_set.add(chosen_node)
            else:
                self._debug_print(f"    No satisfied literal found in Clause #{clause_idx} based on this assignment.")

        self._debug_print(f"Constructed Independent Set: {sorted(independent_set)}\n")
        self._debug_print("Finished sol1tosol2.\n")
        return independent_set

    # def sol2tosol1(self, independent_set):
    def solution2_to_solution1(self, independent_set):
        """
        Convert an Independent Set (set of node_ids) back to a SAT assignment.
        """
        self._debug_print("Starting sol2tosol1 (IS -> SAT) conversion...\n")
        sat_assignment = {}
        formula_list = self.problem1.element.clauses

        # 1. Assign based on selected nodes
        self._debug_print("Assigning variables for selected nodes in the Independent Set.")
        for literal, node in self.input1_to_input2_pairs.items():
            if node in independent_set:
                var = literal.name
                self._debug_print(f" node {node.id} is in the independent set.")
                is_negated = literal.is_negated
                self._debug_print(f"is_negated: {is_negated} for literal: {literal}")
                self.output2_to_output1_pairs[node] = literal  # Reverse mapping

                # If already assigned, skip (to prevent overwriting)
                if var not in sat_assignment:  # not assigned a value yet
                    sat_assignment[var] = not is_negated
                    self._debug_print(
                        f"  Selected node {node.id} => literal {literal}; "
                        f"assigning var {var} = {not is_negated}"
                    )

        # 2. Ensure all variables are assigned
        all_vars = {literal.name for clause in formula_list for literal in clause.variables}
        self._debug_print("\nEnsuring all variables are assigned (default = False).")
        for var in sorted(all_vars):
            if var not in sat_assignment:
                sat_assignment[var] = False
                self._debug_print(
                    f"  var {var} was missing from IS; assigning default value var {var} = False"
                )

        self._debug_print(f"\nFinal recovered SAT Assignment: {sat_assignment}")
        self._debug_print("Finished sol2tosol1.\n")
        return sat_assignment

    def test_solution(self, sat_assignment):
        """
        Check if sat_assignment satisfies the formula, and if it 
        corresponds to a valid independent set in the graph.
        """
        self._debug_print("Starting test_solution...")
        satisfied = self.problem1.evaluate(sat_assignment)
        self._debug_print(f"  Is formula satisfied? {satisfied}")

        chosen = self.solution1_to_solution2(sat_assignment)
        valid_independent = self.problem2.evaluate(chosen)
        self._debug_print(f"  Is chosen set a valid independent set? {valid_independent}")
        self._debug_print("Finished test_solution.\n")

        return satisfied, valid_independent
