import pygame
import random
import numpy as np

from npvis.element import Node, Edge, Graph

# Test code for arbitrary graph display
if __name__ == "__main__":
    # Initialize a graph with nodes, edges, and groups
    nodes = set()
    center = np.array([300, 300])
    radius = 150
    node_count = 12

    # Create nodes
    for i in range(node_count):
        node = Node(node_id=i, name=f"{i}")
        nodes.add(node)

    edges = set()
    node_list = list(nodes)
    groups = []

    # randomly generate edges (around half of all possible edges)
    for i in range(0, node_count):
        for j in range(i + 1, node_count):
            n = random.random()
            if n > 0.5:
                edges.add(Edge(node_list[i], node_list[j]))

    # Initialize and display the graph with bounding box and node radius
    graph = Graph(nodes=nodes, edges=edges, groups=groups, node_radius=20)
    graph.determine_node_positions_nx()
    # start pygame:
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Graph Display")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        graph.display(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()