# three_sat_to_3color_reduction.py
import pygame
import numpy as np
from npvis.reduction.reduction import Reduction
from npvis.problem.three_sat import ThreeSATProblem
from npvis.problem.three_coloring import ThreeColoringProblem  # the class you wrote
from npvis.element import Node, Edge, Variable

class ThreeSatToThreeColoringReduction(Reduction):
    """
    3‑SAT → 3‑Coloring reduction.  
    problem1: ThreeSATProblem  
    problem2: ThreeColoringProblem  
    """

    def __init__(self,
                 three_sat_problem: ThreeSATProblem,
                 three_col_problem: ThreeColoringProblem,
                 debug: bool = False):
        super().__init__(three_sat_problem, three_col_problem)
        self.DEBUG = debug

        # Special “color‐triangle” nodes
        self.base_node   = None
        self.true_node   = None
        self.false_node  = None

        # For each variable name → (positive_node, negative_node)
        self.var_nodes = {}

    def _debug(self, *args):
        if self.DEBUG:
            print("[3SAT→3COL]", *args)

    def build_graph_from_formula(self):
        """
        1) Create the base triangle (Base, True, False).
        2) For each variable x: create x, ¬x, connect them to each other and to Base.
        3) For each clause (ℓ1 ∨ ℓ2 ∨ ℓ3): create a triangle C1,C2,C3 and connect
           Cj to the node representing ℓj.
        """
        col_problem = self.problem2

        # --- Step 1: Base triangle ---
        B = col_problem.add_node("Base")
        T = col_problem.add_node("True")
        F = col_problem.add_node("False")
        for u,v in [(B,T), (T,F), (F,B)]:
            col_problem.add_edge(u, v)

        self.base_node, self.true_node, self.false_node = B, T, F
        self._debug("Created color‐base triangle:", B.id, T.id, F.id)

        # --- Step 2: Variable gadgets ---
        # We iterate over all variables appearing in any clause:
        var_names = sorted({v.name for cl in self.problem1.element.clauses
                                   for v in cl.variables})
        for name in var_names:
            p = col_problem.add_node(f"x{name}")
            n = col_problem.add_node(f"¬x{name}")
            # p—n and both to Base
            col_problem.add_edge(p, n)
            col_problem.add_edge(p, B)
            col_problem.add_edge(n, B)

            self.var_nodes[name] = (p, n)
            self._debug(f"Variable gadget for x{name}: pos={p.id}, neg={n.id}")

        # --- Step 3: Clause gadgets ---
        for c_idx, clause in enumerate(self.problem1.element.clauses):
            c_nodes = []
            for lit_idx, literal in enumerate(clause.variables):
                # Create one clause‐triangle node per literal
                cnode = col_problem.add_node(f"C{c_idx}_{lit_idx}")
                c_nodes.append(cnode)

                # Map back for click‐highlight or solution correspondence
                self.add_input1_to_input2_by_pair(literal, cnode)
                # self.add_input1_to_input2_dict.setdefault(literal, set()).add(cnode)

                # Connect clause node to the appropriate literal gadget‐node
                pos_node, neg_node = self.var_nodes[literal.name]
                lit_n = neg_node if literal.is_negated else pos_node
                col_problem.add_edge(cnode, lit_n)

                self._debug(f"  Clause#{c_idx} literal {literal} → clause‐node {cnode.id}")

            # Fully connect the 3 clause‐nodes into a triangle
            for i in range(3):
                for j in range(i+1, 3):
                    col_problem.add_edge(c_nodes[i], c_nodes[j])
            col_problem.add_group(c_nodes)
            self._debug(f"Formed clause‐triangle for clause #{c_idx}: nodes {[n.id for n in c_nodes]}")

        self._debug("build_graph_from_formula complete.\n")

    def solution1_to_solution2(self, sat_assignment):
        """
        Given a satisfying 3‑SAT assignment var_id→bool,
        color the 3‑color graph accordingly:
          - Base node stays ‘Base’ color
          - Variable nodes: x_i→True if assigned True else False
          - Clause‐triangle: pick the first satisfied literal ℓ_j,
            color its clause‐node = False (so ℓ_j's node must be True),
            then color the other two with Base and True in a way
            that avoids conflict with their literal‐nodes.
        """
        col_prob = self.problem2
        # 1) Reset everything
        col_prob.reset_coloring()

        # 2) Color the special nodes
        Bc, Tc, Fc = self.base_node, self.true_node, self.false_node
        Tc.color = col_prob.allowed_colors[1]
        Fc.color = col_prob.allowed_colors[0]
        Bc.color = col_prob.allowed_colors[2]

        # 3) Color each variable gadget
        for name, (p, n) in self.var_nodes.items():
            val = bool(sat_assignment[int(name)])
            if val:
                p.color = col_prob.allowed_colors[1]  # True
                n.color = col_prob.allowed_colors[0]  # False
            else:
                p.color = col_prob.allowed_colors[0]
                n.color = col_prob.allowed_colors[1]

        # 4) Color each clause gadget
        for c_idx, clause in enumerate(self.problem1.element.clauses):
            # retrieve the three clause‐nodes
            c_nodes = []
            for lit_idx, literal in enumerate(clause.variables):
                # find cnode in input1_to_input2_by_pair
                cnode = next(iter(self.input1_to_input2_dict[literal]))
                c_nodes.append((literal, cnode))
            # find a satisfied literal
            sat_j = next((j for j,(lit,_) in enumerate(c_nodes)
                             if sat_assignment[int(lit.name)] == lit.is_negated), 0)
            # assign c_nodes[sat_j] = False‐color so its literal gadget must be True
            used = set()
            # false color = allowed_colors[0]
            _, c_false = c_nodes[sat_j]
            c_false.color = col_prob.allowed_colors[0]
            used.add(col_prob.allowed_colors[0])
            # the other two must take the remaining two colors in a valid way
            rem_colors = [c for c in col_prob.allowed_colors if c not in used]
            for k,(lit,cnode) in enumerate(c_nodes):
                if k == sat_j:
                    continue
                # choose a color from rem_colors not equal to its literal gadget color
                lit_node = (self.var_nodes[lit.name][0]
                            if not lit.is_negated else
                            self.var_nodes[lit.name][1])
                for color_choice in rem_colors:
                    if color_choice != lit_node.color:
                        cnode.color = color_choice
                        used.add(color_choice)
                        rem_colors.remove(color_choice)
                        break

        # 5) Finally, store the coloring as the solution
        #    group nodes by color to feed NPProblem.display_solution
        color_to_nodes = {}
        for node in col_prob.element.nodes:
            color_to_nodes.setdefault(node.color, set()).add(node)
        sol_sets = list(color_to_nodes.values())
        col_prob.set_solution(sol_sets)

        return sol_sets

    def solution2_to_solution1(self, solution_sets):
        """
        Given a 3‑coloring (list of sets of nodes),
        recover a satisfying SAT assignment var→bool by inspecting
        each variable gadget’s color.
        """
        sat = {}
        for name, (p, n) in self.var_nodes.items():
            # whichever node got the “True” color → variable assignment
            if p.color == self.problem2.allowed_colors[1]:
                sat[int(name)] = True
            else:
                sat[int(name)] = False
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
