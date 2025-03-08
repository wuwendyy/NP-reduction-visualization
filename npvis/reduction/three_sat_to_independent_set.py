class ThreeSatToIndependentSetReduction:
    """
    Performs a standard 3-SAT → Independent Set reduction.

    - build_graph_from_formula(): Creates one node per (literal-occurrence) in each clause.
      Fully connects each clause's nodes, then connects complementary literal-nodes across clauses.
    - sol1tosol2(): Maps a SAT assignment to an Independent Set.
    - sol2tosol1(): Maps an Independent Set back to a SAT assignment.
    """

    def __init__(self, three_sat_problem, ind_set_problem):
        self.three_sat_problem = three_sat_problem
        self.ind_set_problem = ind_set_problem
        self.lit_node_map = {}  # (var_id, is_not_negated, clause_idx) -> node_id
        self.node_lit_map = {}  # node_id -> (var_id, is_not_negated, clause_idx)

    def build_graph_from_formula(self):
        formula_list = self.three_sat_problem.get_as_list()

        # Create nodes per clause and fully connect them.
        for c_idx, clause in enumerate(formula_list):
            clause_nodes = []
            for (var_id, is_not_negated) in clause:
                key = (var_id, is_not_negated, c_idx)
                name = f"x{var_id}" if is_not_negated else f"¬x{var_id}"
                node = self.ind_set_problem.add_node(name=name)
                self.lit_node_map[key] = node.node_id
                self.node_lit_map[node.node_id] = key
                clause_nodes.append(node)

            self.ind_set_problem.add_group(clause_nodes)
            for i in range(len(clause_nodes)):
                for j in range(i + 1, len(clause_nodes)):
                    self.ind_set_problem.add_edge(clause_nodes[i], clause_nodes[j])

        # Connect complementary literal occurrences across clauses.
        graph = self.ind_set_problem.get_graph()
        items = list(self.lit_node_map.items())
        for i in range(len(items)):
            (varA, polA, _cA), nA = items[i]
            nodeA = graph.get_node_by_id(nA)
            for j in range(i + 1, len(items)):
                (varB, polB, _cB), nB = items[j]
                if varA == varB and polA != polB:
                    nodeB = graph.get_node_by_id(nB)
                    self.ind_set_problem.add_edge(nodeA, nodeB)

    def sol1tosol2(self, sat_assignment):
        independent_set = set()
        formula_list = self.three_sat_problem.get_as_list()

        for c_idx, clause in enumerate(formula_list):
            chosen_node = None
            for (var_id, is_not_negated) in clause:
                # Key includes c_idx, so we find the node for this literal occurrence
                key = (var_id, is_not_negated, c_idx)
                node_id = self.lit_node_map.get(key, None)

                # If the assignment matches the literal, consider picking it
                if sat_assignment.get(var_id, False) == is_not_negated:
                    chosen_node = node_id
                    break  # Once we pick a single literal in this clause, we stop

            if chosen_node is not None:
                independent_set.add(chosen_node)

        return independent_set

    def sol2tosol1(self, iset):
        assignment = {}
        for nid in iset:
            if nid in self.node_lit_map:
                var_id, is_not_negated, _cidx = self.node_lit_map[nid]
                assignment[var_id] = is_not_negated
        return assignment

    def test_solution(self, sat_assignment):
        satisfied = self.three_sat_problem.evaluate(sat_assignment)
        chosen = self.sol1tosol2(sat_assignment)
        valid_independent = self.ind_set_problem.is_independent_set(chosen)
        return satisfied, valid_independent
