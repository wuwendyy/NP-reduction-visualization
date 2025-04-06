import pygame
import numpy as np
from npvis.element.formular.clause import Clause
from npvis.element.formular.variable import Variable
from npvis.element.element import Element
from npvis.element.color import LIGHTGREY

class Formula(Element):
    def __init__(self, bounding_box=np.array([[50, 50], [550, 550]])):
        self.clauses = []
        self.bounding_box = bounding_box
        self.original_bounding_box = bounding_box
        self.font = None
        self.literal_rects = {}  # Mapping: (clause_index, literal_index) -> pygame.Rect

    def set_bounding_box(self, bounding_box):
        margin = 10
        # Adjust bounding box so that node centers are confined within an area that
        # leaves a margin of 'node_radius' on all sides.
        adjusted_box = np.array([
            [bounding_box[0][0] + margin, bounding_box[0][1] + margin],
            [bounding_box[1][0] - margin, bounding_box[1][1] - margin]
        ])
        self.bounding_box = adjusted_box
        self.original_bounding_box = bounding_box

    def parse(self, filename):
        """
        Parses a formula from a file in the format:
        (NOT x1 OR x2 OR x3) AND (x2 OR NOT x3 OR x4) AND (x1 OR NOT x2 OR x4)
        """
        self.clauses = []
        counter = 0
        variable_counter = 1  # Unique variable ID

        with open(filename, "r") as f:
            formula_text = f.read().strip()
            clause_texts = formula_text.split("AND")

            for clause_str in clause_texts:
                counter += 1
                clause_str = clause_str.strip()[1:-1]  # Remove parentheses
                clause = Clause(counter)

                tokens = clause_str.split()
                i = 0
                while i < len(tokens):
                    is_negated = False
                    if tokens[i] == "NOT":
                        is_negated = True
                        i += 1  # Move to variable name

                    var_name = tokens[i]
                    variable = Variable(var_name, is_negated, counter, variable_counter)
                    variable_counter += 1
                    clause.add_variable(variable)

                    i += 2  # Skip OR

                self.clauses.append(clause)

    def load_formula_from_tuples(self, list_of_clause_tuples):
        """
        OPTIONAL helper method if you want to load the formula from 
        a Python list of tuples like:
            [ 
              [(1, False), (2, True), (3, True)],
              [(1, True),  (2, False), (3, True)],
              [(1, False), (2, True),  (4, True)]
            ]
        Instead of reading from a file.
        """
        self.clauses = []
        clause_id = 1
        variable_id = 1
        for clause_tuples in list_of_clause_tuples:
            clause_obj = Clause(clause_id)
            for (var_id, is_not_negated) in clause_tuples:
                variable_obj = Variable(str(var_id), is_not_negated, clause_id, variable_id)
                variable_id += 1
                clause_obj.add_variable(variable_obj)
            self.clauses.append(clause_obj)
            clause_id += 1

    def get_as_list(self):
        """
        Return a list of Clause objects so that we can do:
            for clause in formula_list:
                for literal in clause.variables:
                    ...
        """
        return self.clauses

    def evaluate(self, solution):
        return all(clause.evaluate(solution) for clause in self.clauses)

    def display(self, screen):
        if self.font is None:
            self.font = pygame.font.Font(None, 30)
        self.literal_rects.clear()

        x, y = self.bounding_box[0]
        line_height = 30
        current_x = x
        current_y = y

        # For each clause, render its literals and store their bounding rects.
        for c_idx, clause in enumerate(self.clauses):
            # Render opening parenthesis
            open_paren = self.font.render("(", True, LIGHTGREY)
            open_rect = open_paren.get_rect(topleft=(current_x, current_y))
            screen.blit(open_paren, open_rect)
            current_x += open_rect.width

            for l_idx, var in enumerate(clause.variables):
                # Render the variable using its current color.
                lit_surface = self.font.render(str(var), True, var.color)
                lit_rect = lit_surface.get_rect(topleft=(current_x, current_y))
                screen.blit(lit_surface, lit_rect)
                # Store the bounding rectangle for later click detection.
                self.literal_rects[(c_idx, l_idx)] = lit_rect
                current_x += lit_rect.width

                # Add " OR " if not the last literal in the clause.
                if l_idx < len(clause.variables) - 1:
                    or_surface = self.font.render(" OR ", True, LIGHTGREY)
                    or_rect = or_surface.get_rect(topleft=(current_x, current_y))
                    screen.blit(or_surface, or_rect)
                    current_x += or_rect.width

            # Render closing parenthesis.
            closing = ")" if c_idx == len(self.clauses) - 1 else ") AND "
            close_surface = self.font.render(closing, True, LIGHTGREY)
            close_rect = close_surface.get_rect(topleft=(current_x, current_y))
            screen.blit(close_surface, close_rect)
            current_x = self.bounding_box[0][0]  # Reset x for next line.
            current_y += line_height

        # Debug bounding box
        pygame.draw.rect(
            screen,
            LIGHTGREY,
            pygame.Rect(
            self.original_bounding_box[0][0],
            self.original_bounding_box[0][1],
            self.original_bounding_box[1][0] - self.original_bounding_box[0][0],
            self.original_bounding_box[1][1] - self.original_bounding_box[0][1]
            ),
            width=1
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Check if the click falls within any literal's bounding rect.
            for key, rect in self.literal_rects.items():
                if rect.collidepoint(pos):
                    clause_idx, literal_idx = key
                    variable = self.clauses[clause_idx].variables[literal_idx]
                    variable.toggle_highlight()  # Toggle its highlight color.
                    print(f"Variable {variable} in clause {clause_idx} clicked at {pos}.")
    