# this file introduces users to Graph

import numpy as np
from npvis.element import Node, Edge, Graph
import pygame

if __name__ == "__main__":
    # Initialize the pygame window
    pygame.init()
    screen = pygame.display.set_mode((900, 500))
    pygame.display.set_caption("Graph Display Test")
    clock = pygame.time.Clock()

    # Initialize graph and parse from file
    graph_bounding_box = np.array([[100, 100], [400, 400]])
    graph = Graph(set(), set(), None, graph_bounding_box)
    graph.parse("sampleGraph.txt")  # Provide correct file path

    # It is possible to customize graphs with grouping and color options
    custom_graph_bounding_box = np.array([[500, 100], [800, 400]])
    customized_graph = Graph(set(), set(), None, custom_graph_bounding_box)
    customized_graph.parse("sampleGraphGroups.txt")

    # the color of each node can be changed individually
    for node in customized_graph.nodes:
        node.change_color((255, 0, 0))

    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # the graph with default properties, displayed to the left
        graph.display(screen)

        # the graph with groups and custom colors, displayed to the right
        customized_graph.display(screen)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
