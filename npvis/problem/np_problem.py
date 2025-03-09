# This file contains the base class for np problems 
from npvis.element.element import *

class NPProblem:
    """
    Manage the base class structure for NP Problems
    """
    def __init__(self, element = None):
        self.element = element
        self.solution = []
        # a list of colors for each grouped solution 
        self.colors = [
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (255, 255, 0),  # Yellow
            (0, 128, 128),  # Teal
            (139, 69, 19),  # Brown
            (75, 0, 130)    # Indigo
        ]

    def set_element(self, element):
        self.element = element
    
    def set_solution(self, solution):
        self.solution = solution

    def display_problem(self, screen):
        self.element.display(screen)
    
    def display_solution(self, screen):
        # Assumes solutions can be formulated in a list of sets of helpers
        for i in range(len(self.solution)):
            set_solution = self.solution[i]
            for h in set_solution:
                h.change_color(self.colors[i%len(self.colors)])
        self.element.display(screen)


