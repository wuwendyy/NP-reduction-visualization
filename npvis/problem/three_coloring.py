import pygame
import numpy as np
from npvis.element import Graph, Node, Edge
from npvis.problem.np_problem import NPProblem

class ThreeColoringProblem(NPProblem):
    """
    Manages the graph structure for a 3‑Coloring Problem.
    A valid 3‑coloring is one where adjacent nodes have different colors.
    """
    def __init__(self):
        super().__init__(Graph())
        self.next_node_id = 1
        # Define allowed colors: red, green, and blue
        self.allowed_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        # Holds the current coloring: mapping node_id -> color (tuple)
        self.coloring = {}

    def add_node(self, name=None) -> Node:
        """
        Adds a node to the graph with a default color (the first allowed color).
        """
        node_name = name if name is not None else str(self.next_node_id)
        node = Node(self.next_node_id, node_name)
        self.element.add_node(node)
        self.next_node_id += 1
        return node

    def add_edge(self, node1, node2) -> None:
        """
        Adds an edge between two nodes.
        """
        # Basic assertions can be added as needed.
        edge = Edge(node1, node2)
        self.element.add_edge(edge)
        
    def add_group(self, nodes):
        """
        Groups nodes together so that the graph‐layout algorithm
        can arrange them in a compact cluster.
        """
        # sanity checks, if you like:
        assert len(nodes) > 0, "Group must contain at least one node"
        for n in nodes:
            assert n in self.element.nodes, f"{n} not in graph"
        self.element.groups.append(nodes)

    def reset_coloring(self):
        """
        Resets all nodes to the default color.
        """
        for node in self.element.nodes:
            node.color = node.default_color
        self.coloring.clear()

    def evaluate(self) -> bool:
        """
        Evaluates whether the current coloring is a valid 3-coloring.
        Returns True if all adjacent nodes have different colors, False otherwise.
        """
        for edge in self.element.edges:
            if edge.node1.color == edge.node2.color:
                return False
        return True

    def get_graph(self) -> Graph:
        """
        Returns the underlying Graph object.
        """
        return self.element
