# three_sat_to_3color_reduction.py
import pygame
import numpy as np
from npvis.reduction.reduction import Reduction
from npvis.problem.three_sat import ThreeSATProblem
from npvis.problem.three_coloring import ThreeColoringProblem
from npvis.element import Node, Edge, Variable

class ThreeSatToThreeColoringReduction(Reduction):
    def __init__(self,
                 three_sat_problem: ThreeSATProblem,
                 three_col_problem: ThreeColoringProblem,
                 debug: bool = False):
        super().__init__(three_sat_problem, three_col_problem)
        self.DEBUG = debug

        # will hold our 3 “base” nodes
        self.base_node   = None
        self.true_node   = None
        self.false_node  = None

        # variable_name → (positive_node, negative_node)
        self.var_nodes = {}

    def _debug(self, *args):
        if self.DEBUG:
            print("[3SAT→3COL]", *args)

    def build_graph_from_formula(self):
        # Phase 1: the color‐base triangle
        self._build_color_base()

        # Phase 2: one gadget per variable
        self._build_variable_gadgets()

        # Phase 3: one OR‐gadget per clause, built from two XOR sub‐gadgets
        self._build_clause_gadgets()

        self._debug("Finished build_graph_from_formula.\n")

    # ─── PHASE 1 ──────────────────────────────────────────────────────────────
    def _build_color_base(self):
        col = self.problem2
        B = col.add_node("Base")
        T = col.add_node("True")
        F = col.add_node("False")
        for u,v in ((B,T),(T,F),(F,B)):
            col.add_edge(u,v)
        col.add_group([B, T, F])
        self.base_node, self.true_node, self.false_node = B,T,F
        self._debug("Built base triangle:", B.id,T.id,F.id)

    # ─── PHASE 2 ──────────────────────────────────────────────────────────────
    def _build_variable_gadgets(self):
        col = self.problem2
        # extract every variable name from the SAT formula
        var_names = sorted({str(v.name) 
                            for cl in self.problem1.element.clauses 
                            for v in cl.variables})
        for name in var_names:
            p = col.add_node(f"x{name}")
            n = col.add_node(f"¬x{name}")
            # connect p–n and both back to Base
            col.add_edge(p, n)
            col.add_edge(p, self.base_node)
            col.add_edge(n, self.base_node)
            # group each variable-pair together
            col.add_group([p, n])
            
            self.var_nodes[name] = (p,n)
            self._debug(f"Variable gadget x{name}: pos={p.id}, neg={n.id}")

    # ─── PHASE 3 ──────────────────────────────────────────────────────────────
    def _build_clause_gadgets(self):
        col = self.problem2
        for c_idx, clause in enumerate(self.problem1.element.clauses):
            # collect the literal‐gadget nodes in order
            lit_nodes = []
            for lit in clause.variables:
                pos, neg = self.var_nodes[lit.name]
                lit_node = pos if not lit.is_negated else neg
                lit_nodes.append(lit_node)

            # now build the OR(lit1,lit2,lit3) as XOR( XOR(l1,l2), l3 )
            x12 = self._build_xor_gadget(lit_nodes[0], lit_nodes[1])
            x123 = self._build_xor_gadget(x12[-1],    # last node of first XOR
                                          lit_nodes[2])

            # the two XOR calls created 3+3=6 new nodes: x12[0..2], x123[0..2]
            or_nodes = list(x12) + list(x123)            
            for u in or_nodes:
                # register the correspondence for highlighting
                for lit in clause.variables:
                    self.add_input1_to_input2_by_pair(lit, u)
            self._debug(f"Built clause#{c_idx} OR‐gadget: nodes {[n.id for n in or_nodes]}")

    def _build_xor_gadget(self, a: Node, b: Node):
        """
        Create a 3‑node XOR gadget that “computes” a⊕b in a 3‑coloring sense.
        Returns the 3 new nodes in a tuple (g1,g2,g3), where g3 is the final output node.
        You must wire edges here according to your XOR‐gadget design.
        """
        col = self.problem2
        # create 3 new nodes (no name for now)
        g1 = col.add_node("")
        g2 = col.add_node("")
        g3 = col.add_node("")
        
        # Example wiring—replace with your actual gadget:
        col.add_edge(g1, a)
        col.add_edge(g1, b)
        col.add_edge(g2, a)
        col.add_edge(g2, b)
        col.add_edge(g3, g1)
        col.add_edge(g3, g2)
        
        # Group XOR gadget nodes together for layout
        col.add_group([g1, g2, g3])
        
        return g1, g2, g3

    def solution1_to_solution2(self, sat_assignment):
        """
        Given a SAT assignment (var→bool), partition *all* nodes into exactly three
        disjoint sets [S_false, S_true, S_base], hand them to the problem via
        problem2.set_solution(...), and return that list.
        """
        # shorthand
        col_prob = self.problem2

        # prepare the three color‐classes
        S_false = set()  # color‐class 0
        S_true  = set()  # color‐class 1
        S_base  = set()  # color‐class 2

        # 1) special triangle
        S_false.add(self.false_node)
        S_true .add(self.true_node)
        S_base .add(self.base_node)

        # 2) variable gadgets
        for name, (pos, neg) in self.var_nodes.items():
            val = bool(sat_assignment[int(name)])
            if val:
                S_true .add(pos)
                S_false.add(neg)
            else:
                S_false.add(pos)
                S_true .add(neg)

        # 3) clause gadgets
        for clause in self.problem1.element.clauses:
            # collect (literal, clause_node) pairs
            pairs = []
            for lit in clause.variables:
                cnode = next(iter(self.input1_to_input2_dict[lit]))
                pairs.append((lit, cnode))

            # find the first satisfied literal
            winner_idx = next(
                (i for i,(lit,_) in enumerate(pairs)
                 if sat_assignment[int(lit.name)] == lit.is_negated),
                0
            )
            # winner goes into S_false
            _, winner_node = pairs[winner_idx]
            S_false.add(winner_node)

            # the two losers must split {S_base, S_true}
            # start with both as candidates
            candidates = [S_base, S_true]
            for i, (lit, cnode) in enumerate(pairs):
                if i == winner_idx:
                    continue
                # identify which set contains its literal‐node
                lit_node = (self.var_nodes[lit.name][1]
                            if lit.is_negated else
                            self.var_nodes[lit.name][0])

                # pick the first candidate *not* containing lit_node
                chosen = None
                for s in candidates:
                    if lit_node not in s:
                        chosen = s
                        break
                # if somehow both contain lit_node (shouldn't happen), just pick the first
                if chosen is None:
                    chosen = candidates[0]

                chosen.add(cnode)
                candidates.remove(chosen)

        # now hand them off
        solution_sets = [S_false, S_true, S_base]
        col_prob.set_solution(solution_sets)
        return solution_sets

    def solution2_to_solution1(self, solution_sets):
        """
        Given the three color‐classes [S_false, S_true, S_base], recover
        a SAT assignment by checking which “pos”‐node is in S_true.
        """
        # solution_sets[1] is the true‐color class
        true_set = solution_sets[1]
        sat = {}
        for name, (pos, neg) in self.var_nodes.items():
            sat[int(name)] = (pos in true_set)
        return sat
    
    def test_solution(self, sat_assignment):
        """
        1) Check that sat_assignment actually satisfies the 3‑SAT formula.
        2) Run solution1_to_solution2 to color the graph.
        3) Check that the resulting 3‑coloring is valid.
        Returns (formula_satisfied: bool, coloring_valid: bool).
        """
        # 1) formula check
        sat_ok = self.problem1.evaluate(sat_assignment)

        # 2) color the graph from this assignment
        self.solution1_to_solution2(sat_assignment)

        # 3) coloring check
        col_ok = self.problem2.evaluate()

        return sat_ok, col_ok
