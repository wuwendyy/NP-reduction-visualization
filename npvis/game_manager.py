import pygame

class GameManager:
    def __init__(self, width=800, height=600, fps=30):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("NP Problem Display")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.problems = []  # List of tuples: (problem_instance, bounding_box)
        self.running = False
        self.show_solution = False  # Flag to toggle solution display
        self.clicked = set() # List of clicked sub-elements 
        self.reduction = None

    def add_problem(self, problem, bounding_box):
        """
        Registers an NP problem for display and automatically sets its bounding box.
        
        The problem instance should provide a display method, e.g.:
          - display_problem(screen)
          - Optionally, display_solution(screen)
        
        The bounding_box is a 2x2 numpy array.
        """
        if hasattr(problem, 'get_formula'):
            formula = problem.get_formula()
            formula.set_bounding_box(bounding_box)
        if hasattr(problem, 'get_graph'):
            graph = problem.get_graph()
            graph.set_bounding_box(bounding_box)
            graph.determine_node_positions()

        self.problems.append((problem, bounding_box))

    def add_reduction(self, reduction):
        self.reduction = reduction

    def clear_screen(self, color=(255, 255, 255)):
        self.screen.fill(color)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    # Toggle solution display when 's' is pressed
                    self.show_solution = not self.show_solution
                    if not self.show_solution:
                        for problem, _ in self.problems:
                            problem.disable_solution()
                        if self.reduction is not None:
                            self.reduction.display_input_to_input(self.clicked)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for problem, bounding_box in self.problems:
                    # Check if the mouse click is within the problem's bounding box
                    if (bounding_box[0, 0] < event.pos[0] < bounding_box[1, 0] and 
                        bounding_box[0, 1] < event.pos[1] < bounding_box[1, 1]):
                        clicked_element = problem.handle_event(event)
                        if clicked_element is not None:
                            if clicked_element in self.clicked:
                                # unclick it 
                                self.clicked.remove(clicked_element)
                            else:
                                self.clicked.add(clicked_element)
                            if not self.show_solution:
                                self.reduction.display_input_to_input(self.clicked)

    def update_display(self):
        for problem, _ in self.problems:
            if self.show_solution:
                problem.display_solution(self.screen)
            else:
                problem.display_problem(self.screen)

    def run(self):
        self.running = True
        while self.running:
            self.clear_screen()
            self.process_events()
            self.update_display()
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()
