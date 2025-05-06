import pygame
import numpy as np

from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction

def main():
    # Create problems
    three_sat_problem = ThreeSATProblem()

    # Load formula into ThreeSATProblem
    clauses = [
        [(1, False), (2, True), (3, True)],  # (¬x1 ∨ x2 ∨ x3)
        [(1, True), (2, False), (3, True)],  # (x1 ∨ ¬x2 ∨ x3)
        [(1, False), (2, True), (4, True)],  # (¬x1 ∨ x2 ∨ x4)
    ]
    three_sat_problem.load_formula_from_tuples(clauses)

    # Example assignment
    sat_assignment = {1: True, 2: True, 3: False, 4: False}
    print("Is the formula satisfied?", three_sat_problem.evaluate(sat_assignment))
    three_sat_problem.set_solution(sat_assignment)
    print(three_sat_problem.solution)

    # Define bounding boxes for both elements
    formula = three_sat_problem.get_formula()
    formula_bounding_box = np.array([[50, 50], [600, 600]]) 
    formula.set_bounding_box(formula_bounding_box)
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Graph and Formula Display")
    clock = pygame.time.Clock()
    
    # Main loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # Clear screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Display both elements
        three_sat_problem.display_solution(screen)

        pygame.display.flip()
        clock.tick(30)  # Limit FPS to 30

    pygame.quit()

if __name__ == "__main__":
    main()
