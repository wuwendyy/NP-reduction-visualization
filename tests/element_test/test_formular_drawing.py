import pygame
import numpy as np
import math
from npvis.element import Formula

# Test code for formular display
if __name__ == "__main__":
    # Test Formula class parsing and display
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Formula Display Test")
    clock = pygame.time.Clock()

    # Initialize formula and parse from file
    formula_bb = np.array([[20,  50], [380, 750]])
    formula = Formula(formula_bb)
    formula.parse("sampleFormula.txt")  # Provide correct file path

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