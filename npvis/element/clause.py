from npvis.element.variable import Variable

class Clause:
    def __init__(self, clause_id: int):
        self.variables = []
        self.clause_id = clause_id

    def add_variable(self, variable: Variable):
        self.variables.append(variable)

    def evaluate(self, solution):
        return any(solution.get(v.name, False) == v.is_negated for v in self.variables)
