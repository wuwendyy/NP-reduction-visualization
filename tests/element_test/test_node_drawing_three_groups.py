import pygame
import numpy as np
import math

from npvis.element import Node, Edge, Graph

# Test code for graph display
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