import pygame
import numpy as np
from npvis.element import Graph, Node, Edge
from npvis.problem.np_problem import NPProblem
from npvis.game_manager import GameManager

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
        # Set default color
        node.color = self.allowed_colors[0]
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

    def set_coloring(self, color_assignment: dict):
        """
        Sets the color for each node according to a mapping from node_id to either an
        allowed color index (0,1,2) or directly a color tuple.
        """
        for node in self.element.nodes:
            if node.id in color_assignment:
                val = color_assignment[node.id]
                if isinstance(val, int):
                    node.color = self.allowed_colors[val % len(self.allowed_colors)]
                    self.coloring[node.id] = node.color
                elif isinstance(val, (tuple, list)) and len(val) == 3:
                    node.color = tuple(val)
                    self.coloring[node.id] = node.color

    def reset_coloring(self):
        """
        Resets all nodes to the default color.
        """
        for node in self.element.nodes:
            node.color = self.allowed_colors[0]
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

    def display_problem(self, screen):
        """
        Delegates display to the underlying Graph's display method.
        """
        self.element.display(screen)

    def handle_event(self, event):
        """
        Checks for mouse clicks on nodes. When a node is clicked,
        cycles its color to the next allowed color.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = np.array(event.pos)
            for node in self.element.nodes:
                # Use Euclidean distance between the click position and the node center.
                if np.linalg.norm(pos - node.location) <= self.element.node_radius:
                    # Cycle to the next color in allowed_colors.
                    current_color = node.color
                    current_idx = self.allowed_colors.index(current_color)
                    new_idx = (current_idx + 1) % len(self.allowed_colors)
                    node.color = self.allowed_colors[new_idx]
                    self.coloring[node.id] = node.color
                    print(f"Node {node.id} ({node.name}) color changed to {node.color}")

    def display_solution(self, screen):
        """
        Optionally, to display the solution, we can highlight nodes based on their color.
        For instance, if a valid 3-coloring has been set, simply re-display the graph.
        """
        self.element.display(screen)

def main():    
    # Create a ThreeColoringProblem instance
    coloring_problem = ThreeColoringProblem()
    
    # Create a simple graph (for example, a triangle)
    n1 = coloring_problem.add_node("A")
    n2 = coloring_problem.add_node("B")
    n3 = coloring_problem.add_node("C")
    coloring_problem.add_edge(n1, n2)
    coloring_problem.add_edge(n2, n3)
    coloring_problem.add_edge(n3, n1)
    
    # Optionally, set up an initial coloring (default is already the first allowed color)
    # You can also later change the coloring by clicking on nodes.

    # Set up a GameManager and assign a bounding box for display.
    gm = GameManager(width=800, height=600, fps=30)
    graph_bounding_box = np.array([[100, 100], [700, 500]])
    gm.add_problem(coloring_problem, graph_bounding_box)
    
    gm.run()

if __name__ == "__main__":
    main()
