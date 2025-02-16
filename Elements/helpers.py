import numpy as np


class Node:
    def __init__(self, node_id, name, selected="false", color=(0, 0, 255), location=np.array([0, 0])):
        self.node_id = node_id
        self.name = name
        self.selected = selected
        self.color = color
        self.location = location

    def change_color(self, new_color):
        self.color = new_color


class Edge:
    def __init__(self, node1, node2, selected="false", color=(0, 0, 0)):
        self.node1 = node1
        self.node2 = node2
        self.selected = selected
        self.color = color


class Variable:
    def __init__(self, var_id, negate):
        self.var_id = var_id
        self.negate = negate


class Clause:
    variables = []

    def __init__(self, clause_id: int):
        self.variables = []
        self.clause_id = clause_id

    def add_variable(self, variable: Variable):
        self.variables.append(variable)

    def test_print(self):
        print(f"Clause: {self.clause_id}")
        for v in self.variables:
            print(f"ID: {v.var_id}, {v.negate}")

    # given a solution, evaluate if the clause is true
    def evaluate(self, solution):
        result = True
        # for i in range(len(self.variables)):
        #     v = self.variables[i]
        #     b = solution[i]
        #     if v.negate:
        #         result = result or b
        #     else:
        #         result = result or not b

        return result

