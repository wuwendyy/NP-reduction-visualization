from abc import abstractmethod
from helpers import *


class Element:
    # display to pygame
    @abstractmethod
    def display(self):
        pass

    # parse in from file
    @abstractmethod
    def parse(self):
        pass


class Graph(Element):
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    # placeholder print display
    def display(self):
        print("Nodes:")
        for node in self.nodes:
            print(node.node_id)
        print("Edges:")
        for edge in self.edges:
            print(f"( {edge.node1.node_id}, {edge.node2.node_id})")

    def parse(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                pass

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, edge):
        self.edges.add(edge)


class Formula(Element):
    def __init__(self):
        self.clauses = set()
        self.variables = set()

    def display(self):
        pass

    def parse(self):
        pass
