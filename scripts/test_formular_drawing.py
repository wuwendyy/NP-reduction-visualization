import pygame
import numpy as np
import math
from elements import Formula

# Test code for formular display
if __name__ == "__main__":
    # Test Formula class parsing and display
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Formula Display Test")
    clock = pygame.time.Clock()

    # Initialize formula and parse from file
    formula_bounding_box = np.array([[0, 0], [400, 200]])
    formula = Formula(formula_bounding_box)
    formula.parse("sample_elements/sampleFormula.txt")  # Provide correct file path

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