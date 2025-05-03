from npvis.element.formula.variable import Variable
from npvis.element.subelement import SubElement
from npvis.element.color import LIGHTGREY, LIGHTPINK

class Clause(SubElement):
    def __init__(self, clause_id: int):
        SubElement.__init__(self, clause_id, clause_id)
        self.variables = []
        self.clause_id = clause_id
        
        # default & current background color
        self.default_color = LIGHTGREY  # very light grey
        self.color = self.default_color

    def __repr__(self):
        line = "Clause " + str(self.clause_id) + ": "
        for var in self.variables:
            if var.is_negated:
                line = line + "¬"
            line = line + var.name + " OR "
        return line[:-4]

    def add_variable(self, variable: Variable):
        self.variables.append(variable)
        
    def change_color(self, new_color):
        """Set this clause’s background color."""
        self.color = new_color

    def reset_color(self):
        """Restore the default background color."""
        self.color = self.default_color

    def evaluate(self, solution):
        return any(solution[v.name] != v.is_negated for v in self.variables)
    