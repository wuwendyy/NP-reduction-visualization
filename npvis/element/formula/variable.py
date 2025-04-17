from npvis.element.color import LIGHTBLUE, LIGHTPINK

class Variable:
    def __init__(self, name, is_negated, clause_id, var_id, color=LIGHTBLUE):
        self.name = name
        self.is_negated = is_negated
        self.clause_id = clause_id
        self.id = var_id
        self.color = color
        self.default_color = color  # Save the default color

    def change_color(self, new_color):
        self.color = new_color

    def toggle_highlight(self, highlight_color=LIGHTPINK):
        if self.color == self.default_color:
            self.change_color(highlight_color)
        else:
            self.change_color(self.default_color)

    def __str__(self):  
        sign = "" if not self.is_negated else "¬"
        return f"{sign}x{self.name}"

    def __repr__(self):
        return self.__str__()
