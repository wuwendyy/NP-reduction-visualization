class ThreeSatToIndependentSetReduction:
    """
    A single reduction class that uses ThreeSATProblem and IndependentSetProblem.
    The user only writes logic to:
      1) Build a graph from the 3-SAT instance,
      2) Convert SAT solutions to independent sets,
      3) Convert independent sets back to SAT solutions.
    """

    def __init__(self, three_sat_problem, ind_set_problem):
        """
        Initializes the reduction with references to the problem instances.
        """
        self.three_sat_problem = three_sat_problem
        self.ind_set_problem = ind_set_problem
        
        self.lit_node_map = {}
        self.node_lit_map = {}

    def build_graph_from_formula(self):
        """
        Minimal code to transform the 3-SAT formula into the graph structure 
        for an Independent Set problem.
        """
        # Example: For each literal, create a node
        formula_list = self.three_sat_problem.get_as_list()
        for clause in formula_list:
            # Possibly group the nodes belonging to a single clause
            nodes_in_clause = []
            for (var_id, is_not_negated) in clause:
                literal_id = (var_id, is_not_negated)
                node = self.ind_set_problem.add_node(name=str(literal_id))
                self.lit_node_map[literal_id] = node.node_id
                self.node_lit_map[node.node_id] = literal_id
                nodes_in_clause.append(node)
            
            # Example: Fully connect nodes in each clause (triangle, etc.)
            for i in range(len(nodes_in_clause)):
                for j in range(i + 1, len(nodes_in_clause)):
                    self.ind_set_problem.add_edge(nodes_in_clause[i], nodes_in_clause[j])

    def sol1tosol2(self, sat_assignment):
        """
        Convert SAT assignment (dict: var_id -> bool) into an Independent Set solution (set of node_ids).
        """
        independent_set = set()
        
        for literal_id, node_id in self.lit_node_map.items():
            var_id, is_not_negated = literal_id
            # If assignment matches literal, pick that node
            if sat_assignment.get(var_id, False) == is_not_negated:
                independent_set.add(node_id)
        return independent_set

    def sol2tosol1(self, independent_set):
        """
        Convert an Independent Set solution back into a SAT assignment (dict: var_id -> bool).
        """
        sat_assignment = {}
        # For each node in the set, recover its literal
        for node_id in independent_set:
            literal_id = self.node_lit_map.get(node_id)
            if literal_id:
                var_id, is_not_negated = literal_id
                sat_assignment[var_id] = is_not_negated
        return sat_assignment

    def test_solution(self, sat_assignment):
        """
        Quickly check if the 3-SAT is satisfied or if the set is independent
        for debugging or demonstration.
        """
        # Check 3-SAT satisfaction
        satisfied = self.three_sat_problem.evaluate(sat_assignment)
        # Build corresponding IS and check if indeed independent
        is_sol = self.sol1tosol2(sat_assignment)
        is_valid = self.ind_set_problem.is_independent_set(is_sol)
        return satisfied, is_valid
