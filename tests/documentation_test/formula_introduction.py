# this file introduces users to Formula (?)

import numpy as np
from npvis.element import Formula
import pygame

if __name__ == "__main__":
    # Initialize the pygame window
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Formula Display Test")
    clock = pygame.time.Clock()

    # Initialize formula and parse from file
    formula_bounding_box = np.array([[100, 100], [400, 200]])
    formula = Formula(formula_bounding_box)
    formula.parse("sampleFormula.txt")  # Provide correct file path

    # The formula class consists of clauses
    # Each clause is made of variables
    print("Clauses: ")
    for clause in formula.clauses:
        print(clause)

    # The colors used in the display can also be customized
    # To change the color of the clause's bounding box:
    formula.clauses[0].change_color((0, 255, 255))
    # To change the color of a specific variable:
    formula.clauses[0].variables[0].change_color((255, 0, 255))

    running = True
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        formula.display(screen)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
