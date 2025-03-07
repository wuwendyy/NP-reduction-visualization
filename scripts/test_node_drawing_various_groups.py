import pygame
import numpy as np
import math

from npvis.elements import Node, Edge, Graph

# Test code for graph display
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

    # Create edges to form fully connected groups
    edges = set()
    node_list = list(nodes)

    # Create a 3-membered group
    group1 = node_list[:3]
    for a in range(3):
        for b in range(a + 1, 3):
            edges.add(Edge(group1[a], group1[b]))

    # Create a 4-membered group
    group2 = node_list[3:7]
    for a in range(4):
        for b in range(a + 1, 4):
            edges.add(Edge(group2[a], group2[b]))

    # Create a 5-membered group
    group3 = node_list[7:12]
    for a in range(5):
        for b in range(a + 1, 5):
            edges.add(Edge(group3[a], group3[b]))

    # Connect the groups with single edges between one node from each group
    edges.add(Edge(group1[0], group2[0]))
    edges.add(Edge(group2[0], group3[0]))
    edges.add(Edge(group3[0], group1[0]))

    groups = [group1, group2, group3]

    # Initialize and display the graph with bounding box and node radius
    bounding_box = np.array([[0, 0], [600, 600]])
    graph = Graph(nodes=nodes, edges=edges, groups=groups, node_radius=20)
    graph.determine_node_positions_by_groups()
    # start pygame:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
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