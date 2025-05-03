import pygame
import numpy as np
from npvis.element.formula.clause import Clause
from npvis.element.formula.variable import Variable
from npvis.element.element import Element
from npvis.element.color import LIGHTGREY

class Formula(Element):
    def __init__(self, bounding_box=np.array([[50, 50], [550, 550]])):
        self.clauses = []
        self.set_bounding_box(bounding_box)
        self.font = None
        self.literal_rects = {}  # (clause_idx, lit_idx) -> Rect
        self.clause_rects  = {}  # clause_idx -> Rect

    def set_bounding_box(self, bounding_box):
        margin = 20
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
                variable_obj = Variable(var_id, not is_not_negated, clause_id, variable_id)
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

    # this can be removed because the evaluation comes through three_sat class
    def evaluate(self, solution):
        return all(clause.evaluate(solution) for clause in self.clauses)

    def display(self, screen):
        if self.font is None:
            self.font = pygame.font.Font(None, 30)
        self.literal_rects.clear()
        self.clause_rects.clear()

        x0, y0 = self.bounding_box[0]
        line_height = 40
        vertical_padding = 10
        start_x = x0
        current_y = y0

        for c_idx, clause in enumerate(self.clauses):
            clause_x = start_x
            clause_y = current_y
            run_x = clause_x

            # Render "("
            open_surf = self.font.render("(", True, LIGHTGREY)
            open_rect = open_surf.get_rect(topleft=(run_x, current_y))
            screen.blit(open_surf, open_rect)
            run_x += open_rect.width

            # Render each literal + " OR "
            for l_idx, var in enumerate(clause.variables):
                lit_surf = self.font.render(str(var), True, var.color)
                lit_rect = lit_surf.get_rect(topleft=(run_x, current_y))
                screen.blit(lit_surf, lit_rect)
                self.literal_rects[(c_idx, l_idx)] = lit_rect
                run_x += lit_rect.width

                if l_idx < len(clause.variables) - 1:
                    or_surf = self.font.render(" OR ", True, LIGHTGREY)
                    or_rect = or_surf.get_rect(topleft=(run_x, current_y))
                    screen.blit(or_surf, or_rect)
                    run_x += or_rect.width

            # Render ") AND " or ")"
            closing = ") AND " if c_idx < len(self.clauses) - 1 else ")"
            close_surf = self.font.render(closing, True, LIGHTGREY)
            close_rect = close_surf.get_rect(topleft=(run_x, current_y))
            screen.blit(close_surf, close_rect)
            run_x += close_rect.width

            # measure clause width and height
            width = run_x - clause_x + 20
            height = line_height
            cls_bg_x = clause_x - 20 // 2
            cls_bg_y = clause_y - 9

            # --- shaded background with round corners ---
            bg = pygame.Surface((width, height), pygame.SRCALPHA)
            bg.fill((*clause.color, 40))    # semi‐transparent fill
            screen.blit(bg, (cls_bg_x, cls_bg_y))

            # --- rounded‐corner border ---
            border_rect = pygame.Rect(cls_bg_x, cls_bg_y, width, height)
            pygame.draw.rect(
                screen,
                clause.color,
                border_rect,
                width=2,
                border_radius=8   # ↑ round the corners
            )

            # store for click hits
            self.clause_rects[c_idx] = border_rect

            # move down for next clause
            current_y += height + vertical_padding

        # final overall bounding‐box debug
        pygame.draw.rect(
            screen, LIGHTGREY,
            pygame.Rect(
                *self.original_bounding_box[0],
                *(self.original_bounding_box[1] - self.original_bounding_box[0])
            ),
            width=1
        )

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return None

        pos = event.pos
        # 1) check literal first
        for (c_idx, l_idx), rect in self.literal_rects.items():
            if rect.collidepoint(pos):
                return self.clauses[c_idx].variables[l_idx]

        # 2) if none, check clause rectangles
        for c_idx, rect in self.clause_rects.items():
            if rect.collidepoint(pos):
                return self.clauses[c_idx]

        return None
