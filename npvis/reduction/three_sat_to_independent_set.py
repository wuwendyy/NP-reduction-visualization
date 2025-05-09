# --------------------------------------------------
# This module implements the reduction from 3‑SAT to INDEPENDENT‑SET
#
# The public API surfaced by the class `ThreeSatToIndependentSetReduction` is:
#
#   * input1_to_input2() ― create the target graph given a 3‑CNF
#   * solution1_to_solution2()  ― turn a SAT assignment into an ind.‑set
#   * solution2_to_solution1()  ― recover a SAT assignment from an ind.‑set
#   * test_solution()           ― quick helper to verify both directions.
#
# The rest of the class consists of **helper data‑structures** that remember
# how literals map to nodes and vice‑versa, plus an optional debug printer.
#
# --------------------------------------------------

from npvis.reduction.reduction import Reduction
from npvis.problem.independent_set import IndependentSetProblem
from npvis.problem.three_sat import ThreeSATProblem


class ThreeSatToIndependentSetReduction(Reduction):
    """Concrete Reduction: 3‑SAT → INDEPENDENT‑SET

    1.  For every clause *(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)* create three nodes – one per
        literal occurrence – and fully connect them so that at most one
        of them can be picked into an independent set.
    2.  For every pair of complementary literals that appear in the formula
        (e.g. x and ¬x in different clauses) connect the corresponding
        nodes.  This prevents a satisfying assignment from picking both.
    3.  The number k for the Independent‑Set instance is simply the number
        of clauses; a satisfying assignment lets us pick exactly one literal
        per clause, hence k nodes in total.

    This class provides bidirectional conversions so the visualiser can
    highlight how solutions correspond.
    """

    # ---------------------------------------------------------------------
    # Construction 
    # ---------------------------------------------------------------------

    def __init__(self,
                 three_sat_problem: ThreeSATProblem,
                 ind_set_problem: IndependentSetProblem,
                 debug: bool = False):
        """Create a new reduction object.

        Parameters
        ----------
        three_sat_problem : ThreeSATProblem
            The source instance in 3‑CNF we want to reduce.
        ind_set_problem   : IndependentSetProblem
            The *target* graph G (initially empty – nodes/edges added later).
        debug : bool, optional
            If *True*, print verbose tracing information to *stdout*.
        """
        super().__init__(three_sat_problem, ind_set_problem)

        self.input1_to_input2_pairs = {}  # SAT‑literal  → graph‑node

        # Whether debug printing is enabled.
        self.DEBUG = debug

    # ---------------------------------------------------------------------
    # Utility printing helper
    # ---------------------------------------------------------------------
    def _debug_print(self, msg: str):
        if self.DEBUG:
            print("[DEBUG]", msg)

    # ---------------------------------------------------------------------
    # 1.  Build the target graph G from the 3‑SAT formula ϕ
    # ---------------------------------------------------------------------
    def input1_to_input2(self) -> None:
        """Populate *self.problem2* (an IndependentSetProblem) with nodes and
        edges so that **Independent‑Set(G, k=len(clauses))** is equivalent to
        the original **3‑SAT(ϕ)** instance.
        """
        # -- Grab the list of (clause, literals) objects -------------------
        self._debug_print("Starting input1_to_input2…")
        formula_list = self.problem1.element.clauses
        self._debug_print(f"Retrieved formula_list with {len(formula_list)} clause(s).")

        # Iterate over each clause *Cⱼ* and perform steps (node creation &
        # intra‑clause clique).
        for c_idx, clause in enumerate(formula_list, start=1):
            self._debug_print(f"Processing Clause #{c_idx} with {len(clause.variables)} variable(s).")

            clause_nodes = []   # Nodes we create for this clause

            # ---- 1(a) Node creation ------------------------------------
            for literal in clause.variables:
                # Create a *brand new* node in the target graph whose name is
                # the repr() of the literal (e.g. 'x₁', '¬x₂').
                node = self.problem2.element.add_node(repr(literal))

                # Store bidirectional mapping for future conversions / UI.
                self.input1_to_input2_pairs[literal] = node
                self.add_input1_to_input2_by_pair(literal, node)    # clicking the literal will highlight the node
                self.add_input1_to_input2_by_pair(clause, node)     # clicking the clause will highlight the node

                # Trace what we just did
                self._debug_print(f"  -- Added literal/node pair [{literal} : {node}] to maps")
                self._debug_print(f"  Created node '{node.id}' with label '{node.name}' for literal {literal}.")

                # Remember the node so we can fully‑connect them momentarily.
                clause_nodes.append(node)

            # ---- 1(b) Tag nodes that belong to the same clause ----------
            # The visualiser will later display them as a unit (triangle).
            self.problem2.element.add_group(clause_nodes)
            self._debug_print(f"  Added group for Clause #{c_idx}: node IDs {[n.id for n in clause_nodes]}.")

            # ---- 1(c) Intra‑clause **clique** --------------------------
            # Connect every pair inside the clause so that only **one** can
            # be chosen in an independent set.  Because each clause contains
            # exactly 3 literals (3‑CNF) we always create a triangle.
            for i in range(len(clause_nodes)):
                for j in range(i + 1, len(clause_nodes)):
                    self.problem2.element.add_edge(clause_nodes[i], clause_nodes[j])
            self._debug_print(f"  Fully connected the nodes within Clause #{c_idx}.")

        # -----------------------------------------------------------------
        # 2.  Inter‑clause edges between *complementary* literals
        #     (x  vs  ¬x) so they cannot both be selected in the IS.
        #       For every variable xᵢ we create an edge between *each* positive
        #        occurrence (xᵢ) and *each* negative occurrence (¬xᵢ) that live
        #        in different clauses.  This guarantees the graph never lets
        #        us pick both literal‑nodes for the same variable, because that
        #        would violate the “independent‑set” property.
        #
        # ------------------------------------------------------------------
        #   Example:      (x ∨ y ∨ z) ∧ (¬x ∨ ¬y ∨ z)
        #   Because x and ¬x can not both be true, we need to ensure in the independent
        #   set that node x and node ¬x will not both be selected
        #    Edges added
        #        v₀  —  v₃    (x  ↔ ¬x)
        #        v₁  —  v₄    (y  ↔ ¬y)
        # -----------------------------------------------------------------
        self._debug_print("Connecting complementary literal occurrences across clauses…")

        # Because we need to cross‑compare every literal against *later* ones
        # input1_to_input2_pairs :  { literal_obj → node_obj }
        items = list(self.input1_to_input2_pairs.items())
        #               └───┬───┘
        #           each item is  (literal, node)

        # These helper dicts collect **all** positive / negative occurrences
        # so the GUI can colour or highlight them together later.
        name_literal_dict = {}  # 'x' → {literal objects for x},  'x_neg' → {¬x, …}
        name_node_dict    = {}  # 'x' → {node objects   for x},  'x_neg' → {v₃, …}

        for i in range(len(items)):
            literal_A, node_A = items[i]

            # Normalise the key so occurrences fall into exactly two buckets:
            #     'x'      → positive literal  x
            #     'x_neg'  → negative literal ¬x
            name = literal_A.name if not literal_A.is_negated else f"{literal_A.name}_neg"

            # Record this literal / node under its bucket for later use
            # name_literal_dict.setdefault(name, set()).add(literal_A)
            name_node_dict.setdefault(name, set()).add(node_A)

            # Compare with every *later* literal_B (j > i) so each pair is handled once
            for j in range(i + 1, len(items)):
                literal_B, node_B = items[j]

                # SAME variable label   &&   OPPOSITE polarity?  → connect!
                
                # Example   ─ Complementary literals  →  condition is **True**
                # -------------------------------------------------------------
                # literal_A =  x2    (name='x2', is_negated=False)
                # literal_B = ¬x2    (name='x2', is_negated=True)
                #
                # literal_A.name == literal_B.name        →  'x2' == 'x2'       ✔︎
                # literal_A.is_negated != literal_B.is_negated  →  False != True ✔︎
                # Both tests pass, so we add an edge between the two nodes.
                if literal_A.name == literal_B.name and literal_A.is_negated != literal_B.is_negated:
                    self.problem2.element.add_edge(node_A, node_B)
                    self._debug_print(
                        f"  Connected complementary literals '{literal_A}' ↔ '{literal_B}' "
                        f"via nodes {node_A.id} and {node_B.id}.")
                    
        # # The gathered *same‑sign* buckets are now inserted into helper maps
        # # so the visualiser can flash *all* positive occurrences of x together.
        # for name, literals in name_literal_dict.items():
        #     # (Framework call omitted – uncomment if the UI expects it)
        #     self._debug_print(
        #         f"  -- Added same_name_literals/same_name_nodes pair "
        #         f"[{literals} : {name_node_dict[name]}] to maps")

        self._debug_print("Finished input1_to_input2.\n")

    # ---------------------------------------------------------------------
    # 3.  Convert SAT‑assignment → Independent Set
    # ---------------------------------------------------------------------
    def solution1_to_solution2(self):
        """Given a satisfying *sat_assignment* (dict var→bool) return the set
        of graph nodes that constitutes the corresponding **independent set**.

        Notes
        -----
        • Exactly one *satisfied* literal is picked per clause (triangle).
        • Because complementary literals are connected, the set is indeed
          independent as long as the assignment satisfies the formula.
        """
        self._debug_print("Starting sol1_to_sol2 (SAT → IS) conversion…")

        sat_assignment = self.problem1.solution
        print("sat_assignment:", sat_assignment)

        independent_set = set()  # The resulting node set
        formula_list = self.problem1.element.clauses

        # Iterate clause‑by‑clause to choose *one* node per satisfied clause.
        for clause_idx, clause in enumerate(formula_list, start=1):
            chosen_node = None  # Reset for this clause
            self._debug_print(f"  Evaluating Clause #{clause_idx}…")

            for literal in clause.variables:
                # Get the node info corresponding to this literal
                node = self.input1_to_input2_pairs[literal]
                var_id      = literal.name
                is_negated  = literal.is_negated
                assigned_val = sat_assignment[var_id]

                self._debug_print(
                    f"    Checking literal {literal}: assignment[{var_id}]={assigned_val}, "
                    f"is_negated={is_negated}")

                # A literal is satisfied (true) when its sign matches the assignment.
                #   • Positive  literal  x  ⇒  true  if  assigned_val == True
                #   • Negated   literal ¬x  ⇒  true  if  assigned_val == False
                # Hence we include the node exactly when
                #       assigned_val != is_negated
                # where `is_negated` is True for ¬x and False for x.
                if assigned_val != is_negated:
                    chosen_node = node

                    self._debug_print(
                        f"    → Literal {literal} is satisfied; picking node {node.id}.")
                    break  # Only need *one* per clause

            # After scanning the three literals:
            if chosen_node:
                independent_set.add(chosen_node)
            else:
                # Should not happen if *sat_assignment* truly satisfies ϕ
                self._debug_print(f"    No satisfied literal found in Clause #{clause_idx}.")

        self._debug_print(f"Constructed Independent Set: {[n.id for n in independent_set]}\n")
        self._debug_print("Finished sol1tosol2.\n")
        return independent_set

    # ---------------------------------------------------------------------
    # 4.  Convert Independent Set → SAT‑assignment
    # ---------------------------------------------------------------------
    def solution2_to_solution1(self, independent_set):
        """
        Recover a truth assignment for the original 3‑SAT instance
        from the *independent_set* returned by the graph solver.

        Mapping logic
        -------------
        1.  **Selected nodes ⇒ True literal**
            • Every node in the independent set corresponds to one literal
            (stored in ``self.input1_to_input2_pairs``).
            • If the literal is positive  (x)   → assign  x = True
            If the literal is negated  (¬x)  → assign  x = False
            • If the same variable is implied twice we keep the first value
            (the graph guarantees consistency, so it will be identical).

        2.  **Unselected variables ⇒ default False**
            Any variable that never appears in the independent set is
            unconstrained by the reduction; we give it the default value
            ``False`` so the assignment is total.

        Returns
        -------
        dict[str, bool]
            A mapping  { variable_name : truth_value }  that satisfies the
            original formula exactly when the chosen independent set is
            maximal and valid.
        """
        self._debug_print("Starting sol2tosol1 (IS → SAT) conversion…\n")

        sat_assignment = {}
        formula_list = self.problem1.element.clauses

        # ---- 4(a) Positive information: variables forced by selected nodes
        self._debug_print("Assigning variables for selected nodes in the Independent Set.")
        for literal, node in self.input1_to_input2_pairs.items():
            # We only care about nodes that are selected in the solver’s answer.
            if node in independent_set:
                var = literal.name           # e.g.  "x3"
                is_negated = literal.is_negated     # True  for  ¬x3,  False for  x3

                # If several occurrences mention the *same* variable we accept the
                # first assignment we see and silently ignore any duplicates.
                # (The reduction guarantees consistency: duplicates can never
                # demand conflicting values inside a valid independent set.)
                #
                # - Positive  literal  (x)   → variable must be  True
                # - Negated   literal  (¬x)  → variable must be  False
                #
                # So the truth value we need is  (not is_negated).
                
                # dict.setdefault(key, default) in one sentence:
                # ➜ If *key* is in the dict  →  return its current value (do NOT touch the dict).
                # ➜ Otherwise                →  insert key=default, then return default.
                #
                # Therefore the first time we encounter a variable we lock in its truth value;
                # any later occurrences just read the existing entry and leave it unchanged

                sat_assignment.setdefault(var, not is_negated)

                # Verbose debug trace
                self._debug_print(
                    f"  Selected node {node.id} ⇒ literal {literal}; "
                    f"setting {var} = {not is_negated}")

        # ---- 4(b) Default remaining variables to *False* so assignment is total
        all_vars = {lit.name for clause in formula_list for lit in clause.variables}
        self._debug_print("\nEnsuring all variables are assigned (default = False).")
        for var in sorted(all_vars):
            if var not in sat_assignment:
                sat_assignment[var] = False
                self._debug_print(f"  {var} absent from IS; defaulting {var}=False")

        self._debug_print(f"\nFinal recovered SAT Assignment: {sat_assignment}")
        self._debug_print("Finished sol2tosol1.\n")
        return sat_assignment

    # ---------------------------------------------------------------------
    # 5.  Quick self‑check helper (optional, for demos & unit‑tests)
    # ---------------------------------------------------------------------
    def test_solution(self, sat_assignment):
        """Verify a *sat_assignment* by checking **both** sides:

        1.  Does the assignment satisfy the original 3‑CNF □? (using the
            evaluate() method of the ThreeSATProblem wrapper)
        2.  When turned into an independent set via *solution1_to_solution2*,
            is the resulting node set indeed independent in G? (via evaluate())

        Returns
        -------
        (bool, bool)
            • satisfied         – whether ϕ(sat_assignment) = True
            • valid_independent – whether chosen set is independent in G
        """
        self._debug_print("Starting test_solution…")

        # Step 1: formula evaluation
        satisfied = self.problem1.evaluate(sat_assignment)
        self._debug_print(f"  Formula satisfied? {satisfied}")

        # Step 2: graph evaluation
        chosen_set      = self.solution1_to_solution2()
        valid_independent = self.problem2.evaluate(chosen_set)
        self._debug_print(f"  Independent set valid? {valid_independent}")
        self._debug_print("Finished test_solution.\n")

        return satisfied, valid_independent
