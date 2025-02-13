import math
import random
import pygame
import networkx as nx

from element import Graph, Node, Edge

def spring_layout_nodes(graph, width, height):
    """
    Uses networkx's spring_layout to get positions for each node.
    """
    # Convert our custom Graph to a networkx Graph
    G_nx = nx.Graph()
    for node in graph.get_nodes():
        G_nx.add_node(node.node_id)

    for edge in graph.get_edges():
        n1_id = edge.node1.node_id if isinstance(edge.node1, Node) else edge.node1
        n2_id = edge.node2.node_id if isinstance(edge.node2, Node) else edge.node2
        G_nx.add_edge(n1_id, n2_id)

    # Run spring layout
    pos = nx.spring_layout(G_nx, scale=min(width, height) * 0.4, center=(width/2, height/2))

    # Assign back to our Node objects
    for node in graph.get_nodes():
        node.location = (int(pos[node.node_id][0]), int(pos[node.node_id][1]))

class GraphVisualizer:
    def __init__(self, graph, width=800, height=600):
        """
        Responsible for rendering the graph on a PyGame surface.
        - 'graph' is an instance of the Graph class above.
        """
        self.graph = graph
        self.width = width
        self.height = height

        # PyGame initialization
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Graph Visualizer")
        self.clock = pygame.time.Clock()
        self.running = True

        # Optionally store node positions in a dict if not storing them directly in Node
        # e.g., self.positions = {node_id: (x, y), ...}
        # But if you're storing location in the Node class, you can just read from node.location

        # self._auto_layout()  # Attempt an auto-layout or custom layout
        spring_layout_nodes(self.graph, self.width, self.height)

    def _auto_layout(self):
        """
        Assigns (x, y) positions to each node if they don't already have one.
        Here we do something very simple—random placement. 
        You could replace this with a spring layout, circular layout, etc.
        """
        for node in self.graph.get_nodes():
            if node.location is None:
                x = random.randint(50, self.width - 50)
                y = random.randint(50, self.height - 50)
                node.location = (x, y)

    def run(self):
        """
        Main loop: handles events and draws the graph.
        """
        while self.running:
            self._handle_events()
            self._draw_scene()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    def _handle_events(self):
        """
        Checks for user interactions (clicks, quit, etc.).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._handle_click(mouse_pos)

    def _handle_click(self, mouse_pos):
        """
        Example: highlight a node if clicked.
        """
        for node in self.graph.get_nodes():
            x, y = node.location
            radius = 20
            # If click is within the node circle
            if math.dist(mouse_pos, (x, y)) < radius:
                node.selected = not node.selected
                # Toggle color for demonstration
                node.change_color("red" if node.selected else "blue")
                return  # Stop after the first found node

        # Could also detect edge clicks similarly

    def _draw_scene(self):
        """
        Clears the screen and draws nodes and edges.
        """
        self.screen.fill((255, 255, 255))  # White background

        # Draw edges first (so nodes appear on top)
        for edge in self.graph.get_edges():
            node1 = edge.node1 if isinstance(edge.node1, Node) else self.graph.get_node_by_id(edge.node1)
            node2 = edge.node2 if isinstance(edge.node2, Node) else self.graph.get_node_by_id(edge.node2)
            if node1 and node2:
                pygame.draw.line(
                    self.screen,
                    (0, 0, 0),  # black edges
                    node1.location,
                    node2.location,
                    2
                )

        # Draw nodes
        for node in self.graph.get_nodes():
            x, y = node.location
            radius = 20
            color = (0, 0, 255)  # default blue
            if node.color.lower() == "red":
                color = (255, 0, 0)
            elif node.color.lower() == "green":
                color = (0, 255, 0)
            # etc.

            pygame.draw.circle(self.screen, color, (x, y), radius)

            # Optionally draw node name in the center
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(node.name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    # 1) Create a Graph
    graph = Graph()

    # 2) Create some nodes
    node_a = Node(node_id=1, name="A", color="blue")
    node_b = Node(node_id=2, name="B", color="blue")
    node_c = Node(node_id=3, name="C", color="blue")

    # 3) Add them to the graph
    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)

    # 4) Create edges
    edge_ab = Edge(node1=node_a, node2=node_b)
    edge_bc = Edge(node1=node_b, node2=node_c)

    # 5) Add edges
    graph.add_edge(edge_ab)
    graph.add_edge(edge_bc)

    # 6) Visualize
    visualizer = GraphVisualizer(graph)
    visualizer.run()  # starts the PyGame main loop
