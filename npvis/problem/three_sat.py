from npvis.element import Formula, Variable, Clause
from npvis.problem.np_problem import NPProblem

class ThreeSATProblem(NPProblem):
    """
    Manages the 3-SAT formula, providing creation, editing, and evaluation logic.
    No visualization is handled here.
    """

    def __init__(self):
        super().__init__(Formula())
        
    
    def load_formula_from_tuples(self, list_of_clause_tuples):
        self.element.load_formula_from_tuples(list_of_clause_tuples)
            
    def add_clause(self, literals) -> None:
        """
        Adds a clause to the formula.

        Args:
            literals (list): A list of tuples (var_id, is_negated).
                             E.g., [(1, True), (2, False), (3, True)]
        """
        clause_idx = len(self.element.clauses) + 1
        clause_obj = Clause(clause_idx)

        for lit_id, (var_id, is_negated) in enumerate(literals, start=1):
            variable = Variable(var_id, is_negated, clause_idx, lit_id)
            clause_obj.add_variable(variable)

        self.element.clauses.append(clause_obj)

    def load_formula(self, clause_list) -> None:
        """
        Bulk-loads a set of clauses into the formula.

        Args:
            clause_list (list): Each item is a list of (var_id, is_negated).
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
        return all(self._evaluate_clause(clause, assignment) for clause in self.element.clauses)

    def _evaluate_clause(self, clause_obj, assignment) -> bool:
        """
        Evaluates a single clause under a given assignment.
        """
        result = False
        for var in clause_obj.variables:
            # print(f"testing {var.name}, negated = {var.is_negated}")
            # assignment.get(...) defaults to False if variable not in assignment
            if assignment.get(var.name, False) != var.is_negated:
                result = True
                break
        return result

    def get_variables(self) -> set[str]:
        """
        Returns a set of all variable IDs in the formula.
        """
        all_vars = set()
        for clause_obj in self.element.clauses:
            for var in clause_obj.variables:
                all_vars.add(var.name)
        return all_vars

    def get_as_list(self) -> list[list[tuple[str, bool]]]:
        """
        Returns the formula as a list of lists of (var_id, is_negated).
        Helps in interfacing with other modules or for debugging.
        """
        output = []
        for clause_obj in self.element.clauses:
            clause_list = []
            for var in clause_obj.variables:
                clause_list.append((var.name, var.is_negated))
            output.append(clause_list)
        return output
    
    def get_formula(self) -> Formula:
        """
        Returns the underlying Formula object.
        """
        return self.element
    
    def set_solution(self, assignment):
        # constuct solution from assigment: 
        true_set = set()
        false_set = set()
        for clause in self.element.clauses:
            for var in clause.variables:
                is_true = assignment[var.name]
                if var.is_negated:
                    is_true = not is_true
                if is_true:
                    true_set.add(var)
                else:
                    false_set.add(var)
        solution = [true_set, false_set]
        super().set_solution(solution)

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
    three_sat_problem.set_solution(assignment)
    print(three_sat_problem.solution)
