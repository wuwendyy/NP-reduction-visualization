import numpy as np


class Node:
    neighbors = []  # store all neighbor node_id

    def __init__(self, node_id, name, selected="false", color=(0, 0, 255), location=np.array([0, 0])):
        self.node_id = node_id
        self.name = name
        self.selected = selected
        self.color = color
        self.location = location

    def change_color(self, new_color):
        self.color = new_color

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)


class Edge:
    def __init__(self, node1, node2, selected="false", color=(0, 0, 0)):
        self.node1 = node1
        self.node2 = node2
        self.selected = selected
        self.color = color


class SATSolution:
    """
        {'X1': True, 'X2': True, 'X3': False, 'X4': False, 'X5': True}
    """
    solution = {}

    def parse(self, filename):
        with open(filename, "r") as file:
            for line in file:
                x = line.strip().split(": ")
                self.solution[x[0]] = (x[1] == "True")
        file.close()


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

    # given a solution, evaluate if the clause is true
    def evaluate(self, solution: SATSolution):
        result = False
        for v in self.variables:
            assign = solution.solution[v.var_id]
            if v.negate:
                result = result or not assign
            else:
                result = result or assign

        return result
