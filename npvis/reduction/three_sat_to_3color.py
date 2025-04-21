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
        Given a SAT assignment (var→bool), color the 3‑color graph:
          • Base       ← allowed_colors[2]
          • True node  ← allowed_colors[1]
          • False node ← allowed_colors[0]
          • For each variable gadget (p,n):
              – if var=True:  p→True,   n→False
              – else:         p→False,  n→True
          • For each clause gadget, pick the first satisfied literal ℓ_j,
            color its C_j node = False, then color the other two with the
            two remaining colors avoiding conflicts.

        Finally, returns a list of three node‐sets [S₀,S₁,S₂] corresponding
        to allowed_colors[0], allowed_colors[1], allowed_colors[2], and
        also calls three_col_problem.set_solution(...)
        """
        col = self.problem2
        # 1) start neutral
        col.reset_coloring()

        # 2) color the special triangle
        Fc, Tc, Bc = self.false_node, self.true_node, self.base_node
        Fc.color = col.allowed_colors[0]
        Tc.color = col.allowed_colors[1]
        Bc.color = col.allowed_colors[2]

        # 3) variable gadgets
        for name, (p, n) in self.var_nodes.items():
            val = bool(sat_assignment[int(name)])
            if val:
                p.color = col.allowed_colors[1]
                n.color = col.allowed_colors[0]
            else:
                p.color = col.allowed_colors[0]
                n.color = col.allowed_colors[1]

        # 4) clause gadgets
        for clause in self.problem1.element.clauses:
            # collect (literal, its C‐node)
            pairs = []
            for lit in clause.variables:
                # each lit maps to an output from _build_clause_gadgets
                cnode = next(iter(self.input1_to_input2_dict[lit]))
                pairs.append((lit, cnode))

            # pick the first satisfied one
            j = next(
                (i for i,(lit,_) in enumerate(pairs)
                 if sat_assignment[int(lit.name)] == lit.is_negated),
                0
            )
            # color that C_j = False color
            _, cj = pairs[j]
            cj.color = col.allowed_colors[0]
            used = {col.allowed_colors[0]}

            # color the other two with the remaining two colors,
            # avoiding matching their connected literal‐gadget node
            rem = [c for c in col.allowed_colors if c not in used]
            for i,(lit,cnode) in enumerate(pairs):
                if i == j: continue
                lit_node = self.var_nodes[lit.name][0] if not lit.is_negated else self.var_nodes[lit.name][1]
                # pick a color ≠ lit_node.color
                for c in rem:
                    if c != lit_node.color:
                        cnode.color = c
                        rem.remove(c)
                        break

        # 5) group nodes by their *actual* solution color,
        #    ignoring any neutrals that slipped through
        color_to_set = {c: set() for c in self.problem2.allowed_colors}
        for node in self.problem2.element.nodes:
            col = node.color
            if col in color_to_set:
                color_to_set[col].add(node)
            # else:  # neutral or leftover — just skip

        # now build the list in the exact same order
        sol_sets = [
            color_to_set[self.problem2.allowed_colors[0]],
            color_to_set[self.problem2.allowed_colors[1]],
            color_to_set[self.problem2.allowed_colors[2]],
        ]

        # hand it off to NPProblem so display_solution will pick up these sets
        self.problem2.set_solution(sol_sets)
        return sol_sets

    def solution2_to_solution1(self, solution_sets):
        """
        Given three color‐classes [S₀,S₁,S₂], recover a SAT assignment:
          for each variable x:
            if its positive‐node in S₁ (the ‘True’ color), x→True,
            else x→False.
        """
        sat = {}
        # solution_sets[1] is the True‐color class
        true_class = solution_sets[1]
        for name, (p, n) in self.var_nodes.items():
            sat[int(name)] = (p in true_class)
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
