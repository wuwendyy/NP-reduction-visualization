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

    def add_node(self, name) -> Node:
        """
        Adds a node to the graph with a default color (the first allowed color).
        """
        assert name is not None, "Node name cannot be None"
        node = Node(self.next_node_id, name)
        self.element.add_node(node)
        self.next_node_id += 1
        return node

    def add_edge(self, node1, node2) -> None:
        """
        Adds an edge between two nodes.
        """
        # Basic assertions can be added as needed.
        self.element.add_edge(node1, node2)
        
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
        Evaluates whether the current solution (a list of 3 node‐sets) is a valid 3-coloring.
        Returns True if for every edge, its two nodes lie in different sets; False otherwise.
        """
        # Assert that we have a solution
        if not self.solution or len(self.solution) != 3:
            raise ValueError("Solution must be a list of three node sets.")
        
        # build a fast lookup: node -> which group it’s assigned to
        node_to_group = {}
        for grp_idx, node_set in enumerate(self.solution):
            for node in node_set:
                node_to_group[node] = grp_idx

        # check every edge
        for edge in self.element.edges:
            g1 = node_to_group.get(edge.node1, None)
            g2 = node_to_group.get(edge.node2, None)
            # if both endpoints assigned and in the same group, invalid
            if g1 is not None and g1 == g2:
                return False

        return True

    def get_graph(self) -> Graph:
        """
        Returns the underlying Graph object.
        """
        return self.element
