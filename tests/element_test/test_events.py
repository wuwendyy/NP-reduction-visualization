import pygame
import numpy as np
import math
from npvis.element import *

# Function to detect if a point is inside a circle
def is_inside_circle(point, circle_center, radius):
    return np.linalg.norm(point - circle_center) <= radius

class Scene:
    def __init__(self, bounding_box):
        self.bounding_box = bounding_box

    def update(self, event):
        pass

    def render(self, screen):
        pass

class GraphScene(Scene):
    def __init__(self, graph, bounding_box):
        super().__init__(bounding_box)
        self.graph = graph

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = np.array(pygame.mouse.get_pos())
            for node in self.graph.nodes:
                if is_inside_circle(mouse_pos, node.location, self.graph.node_radius):
                    node.change_color((255, 0, 0))  # Change color to red when clicked

    def render(self, screen):
        self.graph.display(screen)

class GameManager:
    def __init__(self, screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Interactive Graph Display")
        self.clock = pygame.time.Clock()
        self.scenes = []

    def add_scene(self, scene):
        self.scenes.append(scene)

    def run(self):
        running = True
        while running:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                for scene in self.scenes:
                    scene.update(event)
            for scene in self.scenes:
                scene.render(self.screen)
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

# Test code for interactive graph display
if __name__ == "__main__":
    # Initialize a graph with nodes, edges, and groups
    nodes = set()
    center = np.array([300, 300])
    radius = 150
    node_count = 39

    # Create nodes
    for i in range(node_count):
        node = Node(node_id=i, name=f"{i}")
        nodes.add(node)

    # Create edges to form 3-membered fully connected groups
    edges = set()
    node_list = list(nodes)

    # Group nodes into 3-membered clusters and connect each group fully
    groups = []
    group_size = 3
    for i in range(0, node_count, group_size):
        group = node_list[i:i + group_size]
        if len(group) == group_size:
            groups.append(group)
            # Fully connect the three nodes in the group
            for a in range(group_size):
                for b in range(a + 1, group_size):
                    edges.add(Edge(group[a], group[b]))

    # Initialize the graph
    bounding_box = np.array([[0, 0], [600, 600]])
    graph = Graph(nodes=nodes, edges=edges, groups=groups, node_radius=20)
    graph.determine_node_positions_by_groups()
    
    # Initialize game manager
    game_manager = GameManager((800, 600))
    graph_scene = GraphScene(graph, bounding_box)
    game_manager.add_scene(graph_scene)
    game_manager.run()