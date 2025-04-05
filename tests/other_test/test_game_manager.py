import pygame
import numpy as np

class GameManager:
    def __init__(self, width=800, height=600, fps=30):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NP Problem Display")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.problems = []  # List of tuples: (problem_instance, bounding_box)
        self.running = False

    def add_problem(self, problem, bounding_box):
        """
        Registers an NP problem for display and automatically sets its bounding box.
        
        The problem instance should provide a display method, e.g.:
          - For ThreeSATProblem, a method display_problem(screen)
          - For IndependentSetProblem, a method display_problem(screen)
        
        The bounding_box is a 2x2 numpy array, e.g.:
          np.array([[x_min, y_min], [x_max, y_max]])
        """
        # If the problem has a method to get its underlying element, we set its bounding box.
        if hasattr(problem, 'get_formula'):
            formula = problem.get_formula()
            formula.set_bounding_box(bounding_box)
        if hasattr(problem, 'get_graph'):
            graph = problem.get_graph()
            graph.set_bounding_box(bounding_box)
            graph.determine_node_positions()

        self.problems.append((problem, bounding_box))

    def clear_screen(self, color=(255, 255, 255)):
        self.screen.fill(color)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Additional event handling (e.g., keyboard input) can be added here.

    def update_display(self):
        """
        Calls the display method of all registered NP problems.
        Each problem is expected to implement a display_problem(screen) method.
        """
        for problem, _ in self.problems:
            problem.display_problem(self.screen)
            # problem.display_solution(self.screen)

    def run(self):
        self.running = True
        while self.running:
            self.clear_screen()
            self.process_events()
            self.update_display()
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()

# Example usage in a main function:

def main():
    # Create your NP problem instances (assumed to be imported from your modules)
    from npvis.problem import ThreeSATProblem, IndependentSetProblem
    from npvis.reduction import ThreeSatToIndependentSetReduction

    # Create problems
    three_sat_problem = ThreeSATProblem()
    ind_set_problem = IndependentSetProblem()

    # Load a formula (example clauses)
    clauses = [
        [(1, False), (2, True), (3, True)],
        [(1, True), (2, False), (3, True)],
        [(1, False), (2, True), (4, True)]
    ]
    three_sat_problem.load_formula_from_tuples(clauses)

    # Create reduction and build graph
    reduction = ThreeSatToIndependentSetReduction(three_sat_problem, ind_set_problem)
    reduction.build_graph_from_formula()

    # Register problems with the GameManager and set their bounding boxes.
    gm = GameManager(width=800, height=600, fps=30)
    # For example, display the formula on the left, and the graph on the right.
    formula_bounding_box = np.array([[20, 50], [380, 550]])
    graph_bounding_box = np.array([[420, 50], [780, 550]])

    gm.add_problem(three_sat_problem, formula_bounding_box)
    gm.add_problem(ind_set_problem, graph_bounding_box)

    # Optionally, you can add additional methods or buttons to clear the screen, etc.
    gm.run()

if __name__ == "__main__":
    main()
