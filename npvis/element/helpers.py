import numpy as np


class Node:
    neighbors = []  # store all neighbor node_id

    def __init__(self, node_id, name, selected="false", color=(0, 0, 255), location=np.array([0, 0])):
        self.node_id = node_id  # unique id
        self.name = name
        self.selected = selected
        self.color = color
        self.location = location

    def change_color(self, new_color):
        self.color = new_color

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        
    def __repr__(self):
        return f"Node(ID={self.node_id}, Name={self.name}, Location={self.location.tolist()}, Neighbors={self.neighbors})"


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
    def __init__(self, name, is_not_negated, clause_id, var_id, color=(0, 0, 0)):
        self.name = name
        self.is_not_negated = is_not_negated
        self.clause_id = clause_id
        self.id = var_id
        self.color = color

    def change_color(self, new_color):
        self.color = new_color

    def __str__(self):
        sign = "" if self.is_not_negated else "¬"
        return f"{sign}x{self.name}"

    def __repr__(self):
        return self.__str__()

class Clause:
    def __init__(self, clause_id: int):
        self.variables = []
        self.clause_id = clause_id

    def add_variable(self, variable: Variable):
        self.variables.append(variable)

    def evaluate(self, solution):
        return any(solution.get(v.name, False) == v.is_not_negated for v in self.variables)
