class Variable:
    def __init__(self, name, is_negated, clause_id, var_id, color=(0, 0, 0)):
        self.name = name
        self.is_negated = is_negated
        self.clause_id = clause_id
        self.id = var_id
        self.color = color
        self.default_color = color

    def change_color(self, new_color):
        self.color = new_color

    def __str__(self):
        sign = "" if not self.is_negated else "¬"
        return f"{sign}x{self.name}"

    def __repr__(self):
        return self.__str__()