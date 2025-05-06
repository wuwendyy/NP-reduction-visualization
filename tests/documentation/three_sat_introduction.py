import pygame
import numpy as np

from npvis.problem import ThreeSATProblem


def main():
    # Create problem
    three_sat_problem = ThreeSATProblem()

    # The 3SAT problem is based on a formula
    three_sat_problem.load_formula_from_file("sampleFormula.txt")

    # optionally, you can also load in a formula directly via a list of tuples
    # this data below is equivalent to the formula specified in the sample file
    three_sat_problem2 = ThreeSATProblem()
    clauses = [
        [("X1", True), ("X2", True), ("X3", False)],  # (x1 ∨ x2 ∨ ¬x3)
        [("X1", True), ("X2", False), ("X4", False)],  # (x1 ∨ ¬x2 ∨ ¬x4)
        [("X1", False), ("X2", False), ("X4", True)],  # (¬x1 ∨ ¬x2 ∨ x4)
    ]
    three_sat_problem2.load_formula_from_tuples(clauses)

    # Example assignment
    sat_assignment_invalid = {"X1": True, "X2": True, "X3": False, "X4": False}
    print("Is the formula satisfied?", three_sat_problem.evaluate(sat_assignment_invalid))
    three_sat_problem.set_solution(sat_assignment_invalid)

    sat_assignment_valid = {"X1": True, "X2": False, "X3": False, "X4": False}
    print("Is the formula satisfied?", three_sat_problem2.evaluate(sat_assignment_valid))
    three_sat_problem2.set_solution(sat_assignment_valid)

    # Define bounding boxes for both elements
    formula = three_sat_problem.get_formula()
    formula_bounding_box = np.array([[100, 100], [400, 400]])
    formula.set_bounding_box(formula_bounding_box)

    formula2 = three_sat_problem2.get_formula()
    formula_bounding_box_2 = np.array([[500, 100], [800, 400]])
    formula2.set_bounding_box(formula_bounding_box_2)

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((900, 500))
    pygame.display.set_caption("Three SAT Problem Display")
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
        three_sat_problem2.display_solution(screen)

        pygame.display.flip()
        clock.tick(30)  # Limit FPS to 30

    pygame.quit()


if __name__ == "__main__":
    main()
