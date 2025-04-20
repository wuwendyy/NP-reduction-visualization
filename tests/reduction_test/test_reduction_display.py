import pygame
import numpy as np

from npvis.problem import ThreeSATProblem, IndependentSetProblem
from npvis.reduction import ThreeSatToIndependentSetReduction

def main():
    # 1) Create problems
    three_sat_problem = ThreeSATProblem()
    ind_set_problem = IndependentSetProblem()

    # 2) Load formula into ThreeSATProblem
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]
    three_sat_problem.load_formula_from_tuples(clauses)

    # 3) Create the reduction
    reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem, 1)

    # 4) Build graph from 3-SAT
    reduction.build_graph_from_formula()

    # 5) Example assignment
    sat_assignment = {1: True, 2: True, 3: False, 4: False}

    # 6) Check solution
    satisfied, is_valid = reduction.test_solution(sat_assignment)
    print("Is 3-SAT satisfied?", satisfied)
    print("Is the corresponding set an independent set?", is_valid)

    # Convert solutions
    is_set = reduction.solution1_to_solution2(sat_assignment)
    print("Independent Set from SAT assignment:", is_set)

    recovered_assignment = reduction.solution2_to_solution1(is_set)
    print("Recovered SAT assignment:", recovered_assignment)
    print("Conversion to SAT Assignment completed!\n")
    
    print("Input1 to Input 2: ", reduction.input1_to_input2_dict)
    # Define bounding boxes for both elements
    graph = ind_set_problem.get_graph()
    formula = three_sat_problem.get_formula()
    graph_bounding_box = np.array([[400, 50], [780, 550]])  # Right side of the window
    formula_bounding_box = np.array([[20, 50], [380, 200]])  # Left upper side
    graph.set_bounding_box(graph_bounding_box)
    graph.determine_node_positions()
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
        ind_set_problem.display_problem(screen)
        three_sat_problem.display_problem(screen)

        pygame.display.flip()
        clock.tick(30)  # Limit FPS to 30

    pygame.quit()

if __name__ == "__main__":
    main()
