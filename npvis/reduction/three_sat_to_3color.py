'''
Reduction from 3-SAT to 3-Coloring using OR gadgets.
Best viewed with notes / images in the documentation_images/reduction folder.
'''
from npvis.reduction.reduction import Reduction
from npvis.problem.three_sat import ThreeSATProblem
from npvis.problem.three_coloring import ThreeColoringProblem
from npvis.element.graph.node import Node

class ThreeSatToThreeColoringReduction(Reduction):
    def __init__(self,
                 three_sat_problem: ThreeSATProblem,
                 three_col_problem: ThreeColoringProblem,
                 debug: bool = False):
        '''
        Notice that we are calling the parent constructor with the two problems.
        The parent constructor initializes some variables that we will use later.
        Recommended to check the parent class for more details.
        '''
        super().__init__(three_sat_problem, three_col_problem)
        self.DEBUG = debug
        
        '''
        ⭐ Notes on class variables:
        for this reduction, we need to create these nodes from 3-SAT formula
        that's why we want to keep track of them in the class instance.
        '''
        # the 3 “base” nodes
        self.base_node: Node  = None
        self.true_node: Node  = None
        self.false_node: Node = None

        # var_name → (pos_node, neg_node)
        self.var_nodes = {}

        # for each clause: ([g1_12, g2_12, out12], [g1_123, g2_123, out123])
        self.clause_outputs = []

    def _debug(self, *args):
        if self.DEBUG:
            print("[3SAT→3COL]", *args)

    def build_graph_from_formula(self):
        '''
        ⭐ Input-to-input mapping logic
        To construct the graph from the 3-SAT formula, we need three things:
        1) The base triangle nodes (Base, True, False)
        2) The variable gadgets (for each variable xᵢ)
        3) The clause gadgets (for each clause Cₖ)
        See each method for details.
        '''
        
        self._build_color_base()
        self._build_variable_gadgets()
        self._build_clause_gadgets()
        self._debug("build_graph_from_formula complete.\n")

    def _build_color_base(self):
        '''
        ⭐ Create the base triangle nodes: Base, True, False
        We then connect them in a triangle and group them together.
        Three edges enforce them to be colored differently (3-coloring).
        One group allows us to treat them as a single unit when displaying...
        '''
        col = self.problem2
        B = col.add_node("Base"); T = col.add_node("True"); F = col.add_node("False")
        for u,v in ((B,T),(T,F),(F,B)):
            col.add_edge(u,v)
        col.add_group([B,T,F])
        self.base_node,self.true_node,self.false_node = B,T,F
        self._debug("Base triangle:", B.id, T.id, F.id)

    def _build_variable_gadgets(self):
        '''
        ⭐ Create variable gadgets for each variable xᵢ
        Each variable gadget consists of two nodes:
          - pos_node: represents xᵢ
          - neg_node: represents ¬xᵢ
        Each variable gadget is connected to the base triangle (both positive and negative nodes).
        This ensures that the variable node is either colored true or false, not base.
        (Currently in display, green is true, red is false, and blue is base.)
        See below comments for details.
        '''
        col = self.problem2
        names = sorted({
            v.name
            for clause in self.problem1.element.clauses
            for v in clause.variables
        })
        for name in names:
            # Add positive and negative nodes for the variable
            p = col.add_node(f"{name}")
            n = col.add_node(f"¬{name}")
            
            # Connect pos and neg nodes => they are different colors
            col.add_edge(p,n)
            
            # Connect both nodes to the base triangle => they are not base color
            col.add_edge(p,self.base_node)
            col.add_edge(n,self.base_node)
            # Thus, they are either true or false.
            
            # Group the variable gadget nodes together for display
            col.add_group([p,n])
            
            # Store the variable nodes in the class instance
            self.var_nodes[name] = (p,n)
            self._debug(f"Var gadget {name}:", p.id, n.id)
        
        '''
        Here, this is also for display...
        We want to allow click→highlight on all variable nodes from each clause
        'add_input1_to_input2_by_pair' ensures that clicking the variable 
        will highlight the created positive and negative variable nodes.
        '''
        for ci, clause in enumerate(self.problem1.element.clauses):
            for lit in clause.variables:
                # We retrieve the positive and negative nodes for the variable
                p, n = self.var_nodes[lit.name]
                
                # Add input-to-input mapping for display (this method comes from the base reduction class)
                self.add_input1_to_input2_by_pair(lit, p)
                self.add_input1_to_input2_by_pair(lit, n)

    def _build_clause_gadgets(self):
        '''
        ⭐ Create clause gadgets for each clause Cₖ
        This is the complicated part of the reduction. 
        How do we 'transfer' the clause satisfiability into the 3-coloring problem?
        We will use a series of OR gadgets to achieve this. let's break it down:
        - Each clause Cₖ has three literals (xᵢ, xⱼ, xₖ).
        - For each clause, we will create a series of OR gadgets that will
          enforce the clause to be satisfied if at least one literal is true.
        See below comments for details.
        '''
        col = self.problem2
        self.clause_outputs = []

        # We iterate over each clause in the 3-SAT problem
        for ci, clause in enumerate(self.problem1.element.clauses):
            '''
            First, we need to find the positive and negative nodes for each literal in the clause
            Remember that we stored these in self.var_nodes (they are created in _build_variable_gadgets)
            lnodes will store one of the positive or negative nodes,
            the one that corresponds to the literal's truth value.
            '''
            lnodes = []
            for lit in clause.variables:
                p,n = self.var_nodes[lit.name]
                lnodes.append(n if lit.is_negated else p)

            '''
            We connects the 'true' nodes of the literals to the OR gadgets.
            We use the _build_or_gadget method to create the OR gadgets. Details in the method.
            Input:
                - lnodes[0]: node for literal 1 (xᵢ or ¬xᵢ)
                - lnodes[1]: node for literal 2 (xⱼ or ¬xⱼ)
            Output:
                - g1_12: first internal node of the OR gadget
                - g2_12: second internal node of the OR gadget
                - out12: output node of the OR gadget
            '''
            g1_12, g2_12, out12 = self._build_or_gadget(lnodes[0], lnodes[1])
            
            '''
            Similarly, we connect the output of the first OR gadget to the third literal's node.
            Now, we use two 'OR gadgets' to ensure that if any of the literals are true,
            the clause will be satisfied.
            Input:
                - out12: output node of the first OR gadget
                - lnodes[2]: node for literal 3 (xₖ or ¬xₖ)
            Output:
                - g1_123: first internal node of the second OR gadget
                - g2_123: second internal node of the second OR gadget
                - out123: output node of the second OR gadget
            '''
            g1_123, g2_123, out123 = self._build_or_gadget(out12, lnodes[2])

            '''
            Now we connect the output of the second OR gadget to the base triangle and the false node.
            This guarantees that the out123 node will be in true color
            The specific logic / proof of why this work is not there in the code,
            but you can check this file: 3-coloring-or-gadget.png in the documentation_images/reduction folder.
            '''
            col.add_edge(out123, self.base_node)
            col.add_edge(out123, self.false_node)

            # record all 6 nodes
            self.clause_outputs.append(
                ([g1_12, g2_12, out12],
                 [g1_123, g2_123, out123])
            )
            
            '''
            This is also for display...
            If the user clicks on the entire clause, we want to highlight these created OR gadgets
            '''
            for or_node in (g1_12, g2_12, out12, g1_123, g2_123, out123):
                self.add_input1_to_input2_by_pair(clause, or_node)

            self._debug(f"Clause#{ci} gadgets:", 
                        [g1_12.id, g2_12.id, out12.id,
                         g1_123.id, g2_123.id, out123.id])

    def _build_or_gadget(self, a: Node, b: Node):
        '''
        ⭐ Construct a 3-node OR gadget in the 3-coloring reduction graph.

        The gadget enforces that the output node is `True` if at least one input node is `True` by
        creating a triangular connectivity pattern.

        Gadget structure (ASCII art):

             a       b
              \     /
               g1---g2
                \   /
                 out

        Edges:
          g1 -> a, g2 -> b, g1 -> g2, g2 -> out, out -> g1.

        Nodes:
          g1: internal node connected to `a`.
          g2: internal node connected to `b`.
          out: output node of the OR gadget.
        '''
        col = self.problem2
        g1  = col.add_node("in1") 
        g2  = col.add_node("in2") 
        out = col.add_node("out")
        
        # connect the two inputs to the internal nodes
        col.add_edge(g1, a)
        col.add_edge(g2, b)
        
        # fully interconnect the trio
        col.add_edge(g1, g2)
        col.add_edge(g2, out)
        col.add_edge(out, g1)

        # group the OR gadget nodes together for display
        col.add_group([out,g2,g1])
        return g1, g2, out

    def solution1_to_solution2(self, sat_assignment):
        '''
        Build and hand off exactly three sets [S_false,S_true,S_base].
        Given the SAT assignment, we determine which nodes belong to each set (aka which color).
        Three colors are:
            - S_false: nodes colored false (red)
            - S_true: nodes colored true (green)
            - S_base: nodes colored base (blue)
        '''
        S_false, S_true, S_base = set(), set(), set()

        '''
        1) Base triangle: remember that we created three nodes in _build_color_base
        This will always be the same coloring regardless of the SAT assignment.
        '''
        S_false.add(self.false_node)
        S_true .add(self.true_node)
        S_base .add(self.base_node)

        '''
        2) Variable gadgets
        For each variable xᵢ, we determine which node (positive or negative) is colored true
            - If the literal is true in the SAT assignment, we add the positive node to S_true / negative node to S_false.
            - If the literal is false in the SAT assignment, we add the negative node to S_true / positive node to S_false.
        '''
        for name,(p,n) in self.var_nodes.items():
            v = bool(sat_assignment[name])
            if v:
                S_true.add(p);   S_false.add(n)
            else:
                S_false.add(p);  S_true.add(n)

        '''
        3) Clause gadgets — hard-coded 8 → 6 mapping
        Prepare our lookup table:
        each key is (v1,v2,v3) and each value is a pair of lists
          ([class for g1_12, class for g2_12, class for out12],
           [class for g1_123, class for g2_123, class for out123])
        where each “class” is one of S_true, S_false or S_base.
        I know this is a bit confusing, 
        but you can check this file: 3-coloring-or-gadget.png in the documentation_images/reduction folder.
        We can "brute-force" the 8 possible combinations of (v1,v2,v3) and show solution-to-solution mapping.
        Though this is less elegant than a more mathematical proof, it is easier to understand.
        '''
        table = {
            # (v1,v2,v3) : ([g1_12,g2_12,out12], [g1_123,g2_123,out123])
            (False, False, False): ([S_base, S_true, S_false],
                                    [S_base, S_base, S_true]),
            (False, False,  True): ([S_base, S_true, S_false],
                                    [S_base,  S_false,  S_true ]),
            (False,  True, False): ([S_base, S_false,  S_true ],
                                    [S_false,  S_base,  S_true ]),
            (False,  True,  True): ([S_true, S_base,  S_false ],
                                    [S_base,  S_false,  S_true ]),
            ( True, False, False): ([S_false,  S_true,  S_base ],
                                    [S_false,  S_base,  S_true ]),
            ( True, False,  True): ([S_base,  S_true,  S_false ],
                                    [S_base,  S_false,  S_true ]),
            ( True,  True, False): ([S_base,  S_false,  S_true ],
                                    [S_false,  S_base,  S_true ]),
            ( True,  True,  True): ([S_base,  S_false,  S_true ],
                                    [S_base,  S_false,  S_true ]),
        }

        for ci, clause in enumerate(self.problem1.element.clauses):
            '''
            We retrieve the OR gadget nodes for this clause from self.clause_outputs.
            Remember that we stored these in _build_clause_gadgets.
            '''
            (g1_12, g2_12, out12), (g1_123, g2_123, out123) = self.clause_outputs[ci]

            '''
            We determine the truth values of the literals in the clause
            We want to know which case we are in the lookup table.
            '''
            l1,l2,l3 = clause.variables
            v1 = (sat_assignment[l1.name] != l1.is_negated)
            v2 = (sat_assignment[l2.name] != l2.is_negated)
            v3 = (sat_assignment[l3.name] != l3.is_negated)

            '''
            We look up the corresponding classes in the table.
            The table returns the color assignment for each OR gadget we created.
                - class12: color assignment for the first OR gadget (g1_12, g2_12, out12)
                - class123: color assignment for the second OR gadget (g1_123, g2_123, out123)
            '''
            class12, class123 = table[(v1,v2,v3)]

            '''
            We assign the nodes of the OR gadgets to the corresponding classes.
            '''
            # assign the first OR-gadget
            for node, target_set in zip((g1_12, g2_12, out12), class12):
                target_set.add(node)

            # assign the second OR-gadget
            for node, target_set in zip((g1_123, g2_123, out123), class123):
                target_set.add(node)
        
        '''
        Finally, we return the three sets of nodes.
        Notice that we abstract "solution" as a list of set of element objects.
        Check how we display the solution in the np problem class (np_problem.py).
        '''
        solution_sets = [S_true, S_false, S_base]
        return solution_sets

    def solution2_to_solution1(self, solution_sets):
        """
        Recover SAT by testing which xᵢ node is in S_true.
        """
        true_set = solution_sets[0]
        sat = {}
        for name,(p,n) in self.var_nodes.items():
            sat[name] = (p in true_set)
        return sat

    def test_solution(self, sat_assignment):
        sat_ok    = self.problem1.evaluate(sat_assignment)
        sol_sets  = self.solution1_to_solution2(sat_assignment)
        self.problem2.set_solution(sol_sets)
        col_ok    = self.problem2.evaluate()
        return sat_ok, col_ok
