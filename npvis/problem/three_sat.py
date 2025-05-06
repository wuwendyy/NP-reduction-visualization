import os
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
        
    def load_formula_from_file(self, filename: str):
        self.element.parse(filename)

    def evaluate(self, assignment) -> bool:
        """
        Evaluates this 3-SAT formula given a variable assignment.

        Args:
            assignment (dict): Mapping variable_id -> bool

        Returns:
            bool: True if formula is satisfied, otherwise False.
        """
        return all(clause.evaluate(assignment) for clause in self.element.clauses)

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

    def display_solution(self, screen):
        for clause in self.element.clauses:
            clause.color = clause.highlight_color
        super().display_solution(screen)

    def disable_solution(self):
        for clause in self.element.clauses:
            clause.color = clause.default_color
        super().disable_solution()

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
