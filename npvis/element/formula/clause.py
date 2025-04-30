from npvis.element.formula.variable import Variable
from npvis.element.subelement import SubElement


class Clause(SubElement):
    def __init__(self, clause_id: int):
        SubElement.__init__(self, clause_id, clause_id)
        self.variables = []
        self.clause_id = clause_id

    def add_variable(self, variable: Variable):
        self.variables.append(variable)

    def evaluate(self, solution):
        # a clause is satisfied if ANY literal is true,
        # i.e. assignment != is_negated
        return any(solution[v.name] != v.is_negated for v in self.variables)
