# this file introduces users to Independent Set

import numpy as np
from npvis.element import Graph
from npvis.problem import IndependentSetProblem
import pygame

if __name__ == "__main__":
    # Initialize the pygame window
    pygame.init()
    screen = pygame.display.set_mode((1200, 600))
    pygame.display.set_caption("Independent Set Display Test")
    clock = pygame.time.Clock()

    # Initialize graph and parse from file
    graph_bounding_box = np.array([[100, 100], [500, 500]])
    graph = Graph(set(), set(), None, graph_bounding_box)
    graph.parse("sampleGraph.txt")  # Provide correct file path

    ind_set_problem = IndependentSetProblem()
    ind_set_problem.element = graph

    valid_solution = [1, 2, 8]
    invalid_solution = [1, 7]

    # Test if the given solutions are valid
    print("Evaluating Solution 1: ")
    print(ind_set_problem.evaluate(valid_solution))

    print("Evaluating Solution 2: ")
    print(ind_set_problem.evaluate(invalid_solution))

    ind_set_problem.set_solution_by_id(valid_solution)
    ind_set_problem.display_solution(screen)

    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    # disable solution display when 'x' is pressed
                    ind_set_problem.disable_solution()
                if event.key == pygame.K_s:
                    # disable solution display when 's' is pressed
                    ind_set_problem.display_solution(screen)
        # the graph with default properties, displayed to the left
        graph.display(screen)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
