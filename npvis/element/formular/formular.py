import pygame
import numpy as np
from npvis.element.formular.clause import Clause
from npvis.element.formular.variable import Variable
from npvis.element.element import Element

class Formula(Element):
    def __init__(self, bounding_box=np.array([[50, 50], [550, 550]])):
        self.clauses = []
        self.bounding_box = bounding_box
        self.font = None
        self.literal_rects = {}  # Mapping: (clause_index, literal_index) -> pygame.Rect
        self.DEBUG = True

    def set_bounding_box(self, bounding_box):
        self.bounding_box = bounding_box

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
            self.font = pygame.font.Font(None, 24)

        x, y = self.bounding_box[0]
        max_width = self.bounding_box[1][0] - x
        max_height = self.bounding_box[1][1] - y
        line_height = 30  # Height per line
        current_y = y
        default_color = (0, 0, 0)

        for c, clause in enumerate(self.clauses):
            or_surface = self.font.render("(", True, default_color)
            screen.blit(or_surface, (x, y))
            x += or_surface.get_width()
            for i, var in enumerate(clause.variables):
                # Render variable with its own color (assumes var.color is an (R,G,B) tuple)
                var_surface = self.font.render(str(var), True, var.color)
                screen.blit(var_surface, (x, y))
                word_width = var_surface.get_width()
                x += word_width
                # Add " OR " if not the last variable
                if i < len(clause.variables) - 1:
                    or_surface = self.font.render(" OR ", True, default_color)
                    screen.blit(or_surface, (x, y))
                    word_width = or_surface.get_width()
                elif c < len(self.clauses) - 1:
                    or_surface = self.font.render(") AND ", True, default_color)
                    screen.blit(or_surface, (x, y))
                    word_width = or_surface.get_width()
                else:
                    or_surface = self.font.render(")", True, default_color)
                    screen.blit(or_surface, (x, y))
                    word_width = or_surface.get_width()

                x += word_width
                # If the word doesn't fit in the current line, move to the next line
                if x > self.bounding_box[1][0]:
                    x = self.bounding_box[0][0]
                    y += line_height
                    
            # temp_surface = screen.font.render(current_line + (" AND " if current_line else "") + clause, True, (0, 0, 0))
            # temp_width = temp_surface.get_width()

        #     if x > max_width:
        #         if not current_line:
        #             raise ValueError(f"Clause '{clause}' is too wide to fit in bounding box.")

        #         text_lines.append(current_line)
        #         current_line = clause
        #     else:
        #         current_line += (" AND " if current_line else "") + clause

        # if current_line:
        #     text_lines.append(current_line)

        # if len(text_lines) * line_height > max_height:
        #     raise ValueError("Not enough space to display all clauses within the bounding box.")

        # for i, line in enumerate(text_lines):
        #     text_surface = self.font.render(line, True, (0, 0, 0))
        #     screen.blit(text_surface, (x, current_y + i * line_height))
        
        # Debug bounding box
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(self.bounding_box[0][0], self.bounding_box[0][1],
                                                        self.bounding_box[1][0]-self.bounding_box[0][0],
                                                        self.bounding_box[1][1]-self.bounding_box[0][1]), 1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Check if click falls within any literal's rectangle
            for key, rect in self.literal_rects.items():
                if rect.collidepoint(pos):
                    print(f"Literal in clause {key[0]}, index {key[1]} was clicked at {pos}.")
                    # Add additional handling here (e.g., highlighting the literal)
