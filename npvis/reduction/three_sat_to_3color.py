# three_sat_to_3color_reduction.py
import numpy as np
from npvis.reduction.reduction import Reduction
from npvis.problem.three_sat import ThreeSATProblem
from npvis.problem.three_coloring import ThreeColoringProblem
from npvis.element.graph.node import Node

class ThreeSatToThreeColoringReduction(Reduction):
    """
    3‑SAT → 3‑Coloring via chained 3‑node OR gadgets.
    """

    def __init__(self,
                 three_sat_problem: ThreeSATProblem,
                 three_col_problem: ThreeColoringProblem,
                 debug: bool = False):
        super().__init__(three_sat_problem, three_col_problem)
        self.DEBUG = debug

        # the 3 “base” nodes
        self.base_node  = None
        self.true_node  = None
        self.false_node = None

        # var_name → (pos_node, neg_node)
        self.var_nodes = {}

        # for each clause: ([g1_12, g2_12, out12], [g1_123, g2_123, out123])
        self.clause_outputs = []

    def _debug(self, *args):
        if self.DEBUG:
            print("[3SAT→3COL]", *args)

    def build_graph_from_formula(self):
        self._build_color_base()
        self._build_variable_gadgets()
        self._build_clause_gadgets()
        self._debug("build_graph_from_formula complete.\n")

    def _build_color_base(self):
        col = self.problem2
        B = col.add_node("Base"); T = col.add_node("True"); F = col.add_node("False")
        for u,v in ((B,T),(T,F),(F,B)):
            col.add_edge(u,v)
        col.add_group([B,T,F])
        self.base_node,self.true_node,self.false_node = B,T,F
        self._debug("Base triangle:", B.id, T.id, F.id)

    def _build_variable_gadgets(self):
        col = self.problem2
        names = sorted({
            str(v.name)
            for clause in self.problem1.element.clauses
            for v in clause.variables
        })
        for name in names:
            p = col.add_node(f"x{name}")
            n = col.add_node(f"¬x{name}")
            col.add_edge(p,n)
            col.add_edge(p,self.base_node)
            col.add_edge(n,self.base_node)
            col.add_group([p,n])
            self.var_nodes[name] = (p,n)
            self._debug(f"Var gadget {name}:", p.id, n.id)
        
        # allow click→highlight on both gadget‑outputs
        for ci, clause in enumerate(self.problem1.element.clauses):
            for lit in clause.variables:
                p, n = self.var_nodes[lit.name]
                self.add_input1_to_input2_by_pair(lit, p)
                self.add_input1_to_input2_by_pair(lit, n)

    def _build_clause_gadgets(self):
        col = self.problem2
        self.clause_outputs = []

        for ci, clause in enumerate(self.problem1.element.clauses):
            # gather the three literal‐nodes
            lnodes = []
            for lit in clause.variables:
                p,n = self.var_nodes[lit.name]
                lnodes.append(n if lit.is_negated else p)

            # build OR₁ = OR(l1,l2)
            g1_12, g2_12, out12 = self._build_or_gadget(lnodes[0], lnodes[1])
            # build OR₂ = OR(out12,l3)
            g1_123, g2_123, out123 = self._build_or_gadget(out12, lnodes[2])

            # enforce OR₂ → True
            col.add_edge(out123, self.base_node)
            col.add_edge(out123, self.false_node)

            # record all 6 nodes
            self.clause_outputs.append(
                ([g1_12, g2_12, out12],
                 [g1_123, g2_123, out123])
            )
            
            # allow click→highlight on all OR nodes from each clause
            for or_node in (g1_12, g2_12, out12, g1_123, g2_123, out123):
                self.add_input1_to_input2_by_pair(clause, or_node)

            self._debug(f"Clause#{ci} gadgets:", 
                        [g1_12.id, g2_12.id, out12.id,
                         g1_123.id, g2_123.id, out123.id])

    def _build_or_gadget(self, a: Node, b: Node):
        """
        Returns (g1,g2,out) for a small 3‑node OR gadget.
        """
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

        col.add_group([out,g2,g1])
        return g1, g2, out

    def solution1_to_solution2(self, sat_assignment):
        """
        Build and hand off exactly three sets [S_false,S_true,S_base].
        """
        S_false, S_true, S_base = set(), set(), set()

        # 1) Base triangle
        S_false.add(self.false_node)
        S_true .add(self.true_node)
        S_base .add(self.base_node)

        # 2) Variable gadgets
        for name,(p,n) in self.var_nodes.items():
            v = bool(sat_assignment[int(name)])
            if v:
                S_true.add(p);   S_false.add(n)
            else:
                S_false.add(p);  S_true.add(n)

        # 3) Clause gadgets — hard-coded 8 → 6 mapping
        # Prepare our lookup table:
        # each key is (v1,v2,v3) and each value is a pair of lists
        #   ([class for g1_12, class for g2_12, class for out12],
        #    [class for g1_123, class for g2_123, class for out123])
        # where each “class” is one of S_true, S_false or S_base.
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
            (g1_12, g2_12, out12), (g1_123, g2_123, out123) = self.clause_outputs[ci]

            # compute the three literal values
            l1,l2,l3 = clause.variables
            v1 = (sat_assignment[int(l1.name)] != l1.is_negated)
            v2 = (sat_assignment[int(l2.name)] != l2.is_negated)
            v3 = (sat_assignment[int(l3.name)] != l3.is_negated)

            # look up which class each node goes into
            class12, class123 = table[(v1,v2,v3)]

            # assign the first OR-gadget
            for node, target_set in zip((g1_12, g2_12, out12), class12):
                target_set.add(node)

            # assign the second OR-gadget
            for node, target_set in zip((g1_123, g2_123, out123), class123):
                target_set.add(node)
        
        # hand off
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
