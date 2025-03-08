from npvis.element.element import Formula, Variable, Clause

class ThreeSATProblem:
    """
    Manages the 3-SAT formula, providing creation, editing, and evaluation logic.
    No visualization is handled here.
    """

    def __init__(self):
        self.formula = Formula()

    def add_clause(self, literals) -> None:
        """
        Adds a clause to the formula.

        Args:
            literals (list): A list of tuples (var_id, is_not_negated).
                             E.g., [(1, True), (2, False), (3, True)]
        """
        clause_idx = len(self.formula.clauses) + 1
        clause_obj = Clause(clause_idx)

        for lit_id, (var_id, is_not_negated) in enumerate(literals, start=1):
            variable = Variable(var_id, is_not_negated, clause_idx, lit_id)
            clause_obj.add_variable(variable)

        self.formula.clauses.append(clause_obj)

    def load_formula(self, clause_list) -> None:
        """
        Bulk-loads a set of clauses into the formula.

        Args:
            clause_list (list): Each item is a list of (var_id, is_not_negated).
                                E.g., [[(1, False), (2, True), (3, True)], ...]
        """
        for clause in clause_list:
            self.add_clause(clause)

    def evaluate(self, assignment) -> bool:
        """
        Evaluates this 3-SAT formula given a variable assignment.

        Args:
            assignment (dict): Mapping variable_id -> bool

        Returns:
            bool: True if formula is satisfied, otherwise False.
        """
        return all(self._evaluate_clause(clause, assignment) for clause in self.formula.clauses)

    def _evaluate_clause(self, clause_obj, assignment) -> bool:
        """
        Evaluates a single clause under a given assignment.
        """
        result = False
        for var in clause_obj.variables:
            # assignment.get(...) defaults to False if variable not in assignment
            if assignment.get(var.name, False) == var.is_not_negated:
                result = True
                break
        return result

    def get_variables(self) -> set[str]:
        """
        Returns a set of all variable IDs in the formula.
        """
        all_vars = set()
        for clause_obj in self.formula.clauses:
            for var in clause_obj.variables:
                all_vars.add(var.name)
        return all_vars

    def get_as_list(self) -> list[list[tuple[str, bool]]]:
        """
        Returns the formula as a list of lists of (var_id, is_not_negated).
        Helps in interfacing with other modules or for debugging.
        """
        output = []
        for clause_obj in self.formula.clauses:
            clause_list = []
            for var in clause_obj.variables:
                clause_list.append((var.name, var.is_not_negated))
            output.append(clause_list)
        return output
    
    def get_formula(self) -> Formula:
        """
        Returns the underlying Formula object.
        """
        return self.formula

if __name__ == "__main__":
    # Example usage
    three_sat_problem = ThreeSATProblem()
    # Suppose we have a list of clauses:
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]
    three_sat_problem.load_formula(clauses)

    # Evaluate assignment
    assignment = {1: True, 2: True, 3: False, 4: False}
    print("Is the formula satisfied?", three_sat_problem.evaluate(assignment))
