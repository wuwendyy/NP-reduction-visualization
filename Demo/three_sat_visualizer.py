import math
import pygame
from three_sat_reduction import ThreeSatToIndependentSetReduction

# Basic PyGame / drawing constants
WIDTH, HEIGHT = 800, 600
# Colors for visualization
BACKGROUND_COLOR = (255, 255, 255)  # White background
NODE_COLOR = (34,139,34)  # Blue nodes (adjust as needed)
EDGE_COLOR = (0, 0, 0)  # Black edges
LABEL_COLOR = (0, 0, 0)  # Black text for visibility
HIGHLIGHT_NODE_COLOR = (255, 100, 100)  # Red highlight for selected nodes
HIGHLIGHT_COLOR = (255, 100, 100)  # Red highlight for selected nodes

RADIUS = 20

class ThreeSatGraphVisualizer:
    def __init__(self, graph, clause_vertices, formula, literal_to_formula_indices, literal_id_to_node_id, reduction, width=1000, height=700):
        """
        Args:
            graph: NetworkX graph containing 3-SAT nodes/edges.
            clause_vertices: List of lists (node IDs for each clause).
            formula: The original 3-SAT formula.
            literal_to_formula_indices: Mapping from (var, neg) to positions in formula for highlighting.
            width: Width of the PyGame window.
            height: Height of the PyGame window.
        """
        self.graph = graph
        self.clause_vertices = clause_vertices
        self.formula = formula
        self.literal_to_formula_indices = literal_to_formula_indices  # Mapping for highlighting
        self.edge_highlight = None  # Track the selected edge
        self.width = width
        self.height = height
        self.reduction = reduction
        self.literal_id_to_node_id = literal_id_to_node_id  # Added literal_id to node_id mapping

        # Initialize PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3-SAT Graph Visualizer")
        self.clock = pygame.time.Clock()

        
        self.node_highlight = None  # Keeps track of which node is selected
        self.edge_highlight = None  # Keeps track of which edge is selected
        self.highlighted_literals = set()  # Stores which literals to highlight in the formula
        self.highlighted_operators = set()  # ✅ Stores the clause indices where `∨` should be highlighted


        # Compute layout
        self.pos = self._layout_clauses(start_x=150, start_y=350, x_gap=250, radius=80)
        self.running = True


    def _layout_clauses(self, start_x=150, start_y=350, x_gap=250, radius=80):
        """
        Layout function that places each clause as a triangle.
        """
        pos = {}
        for c_idx, clause in enumerate(self.formula):
            center_x = start_x + c_idx * x_gap
            center_y = start_y

            n_lits = len(clause)
            for i, node_id in enumerate(self.clause_vertices[c_idx]):
                angle = 2 * math.pi * i / n_lits
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)

                pos[node_id] = (center_x + x_offset, center_y + y_offset)

        return pos

    def run(self):
        """
        Main event loop for visualization.
        """
        while self.running:
            self._handle_events()
            self._draw_scene()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


    def _handle_events(self):
        """
        Handles user interactions, distinguishing between node and edge clicks.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                print("Mouse clicked at:", mouse_pos)  # ✅ Debugging click events

                # First, check if a node was clicked
                clicked_node = self._handle_node_click(mouse_pos)
                
                if clicked_node is None:
                    # If no node was clicked, check for an edge click
                    self._handle_edge_click(mouse_pos)
                else:
                    # ✅ Node was clicked, so don't process edge clicks
                    self.edge_highlight = None  

    # def _handle_node_click(self, mouse_pos):
    #     """
    #     Detects if a user clicks on a node and highlights it.
    #     Calls `_update_highlighted_literals()` to highlight the corresponding literal in the formula.
    #     """
    #     mx, my = mouse_pos
    #     for node in self.graph.nodes():
    #         x, y = self.pos[node]

    #         # Check if the click is inside the node (circle with radius 25)
    #         if math.sqrt((mx - x) ** 2 + (my - y) ** 2) < 25:
    #             print(f"Node clicked: {node}")  # ✅ Debugging node clicks
    #             self.node_highlight = node  # ✅ Store highlighted node

    #             # ✅ Update highlighted literals
    #             lit = self.graph.nodes[node]["literal"]
    #             self._update_highlighted_literals([lit])

    #             return node  # ✅ Return the clicked node

    #     self.node_highlight = None  # ✅ If no node clicked, clear highlight
    #     self.highlighted_literals.clear()  # ✅ Clear formula highlights when clicking empty space
    #     return None

    def _handle_node_click(self, mouse_pos):
        """
        Detects if a user clicks on a node and highlights it.
        Calls `_update_highlighted_literals()` to highlight the corresponding literal in the formula.
        """
        mx, my = mouse_pos
        for node in self.graph.nodes():
            x, y = self.pos[node]

            # Check if the click is inside the node (circle with radius 25)
            if math.sqrt((mx - x) ** 2 + (my - y) ** 2) < 25:
                print(f"Node clicked: {node}")  # ✅ Debugging node clicks
                self.node_highlight = node  # ✅ Store highlighted node

                # ✅ Extract the literal and its clause index
                lit = self.graph.nodes[node]["literal"]
                
                self._update_highlighted_literals([lit])
                # ✅ Pass the clause-specific literal to `_update_highlighted_literals()`
                # self._update_highlighted_literals([(clause_idx, lit_idx)])

                return node  # ✅ Return the clicked node

        self.node_highlight = None  # ✅ If no node clicked, clear highlight
        self.highlighted_literals.clear()  # ✅ Clear formula highlights when clicking empty space
        return None


    def _handle_edge_click(self, mouse_pos):
        """
        Detects if a user clicks on an edge (curved or straight) and highlights it.
        """
        mx, my = mouse_pos
        self.edge_highlight = None  # ✅ Reset edge highlight if no edge is clicked
        self.highlighted_literals.clear()  # ✅ Clear previous highlights

        closest_edge = None
        min_distance = float('inf')

        for u, v in self.graph.edges():
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            # ✅ Check if edge is curved
            if self._is_curved_edge(u, v):
                # ✅ Check click distance from Bezier curve
                control_x, control_y = self._get_control_point(x1, y1, x2, y2)
                distance = self._distance_to_bezier((x1, y1), (control_x, control_y), (x2, y2), (mx, my))
            else:
                # ✅ Use closest point detection for straight edges
                px, py = self._closest_point_on_segment(x1, y1, x2, y2, mx, my)
                if not self._is_between(x1, y1, x2, y2, px, py):
                    continue
                distance = math.sqrt((px - mx) ** 2 + (py - my) ** 2)

            # ✅ Ensure click precision
            if distance < min_distance and distance < 15:  # Adjust click precision threshold
                min_distance = distance
                closest_edge = (u, v)

        if closest_edge:
            self.edge_highlight = closest_edge
            print(f"Edge clicked: {closest_edge}")  # ✅ Debugging clicked edges

            # ✅ Highlight corresponding literals in the formula
            lit1 = self.graph.nodes[closest_edge[0]]["literal"]
            lit2 = self.graph.nodes[closest_edge[1]]["literal"]
            self._update_highlighted_literals([lit1, lit2])

    def _is_curved_edge(self, u, v):
        """
        Determines if an edge between nodes u and v is curved.
        """
        for node in self.graph.nodes():
            if node != u and node != v:
                x, y = self.pos[node]
                if self._is_edge_passing_through((self.pos[u], self.pos[v]), (x, y)):
                    return True
        return False


    def _get_control_point(self, x1, y1, x2, y2):
        """
        Returns the control point for a curved edge's Bezier curve.
        """
        return (x1 + x2) / 2 + 40, (y1 + y2) / 2 - 40  # Offset for smooth curvature

    def _distance_to_bezier(self, p0, p1, p2, click):
        """
        Computes the distance from a point (click) to a quadratic Bezier curve.
        Uses iterative point sampling to approximate the closest distance.
        """
        min_dist = float('inf')
        for t in range(0, 21):  # Sample along the Bezier curve
            t /= 20.0
            bx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            by = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]

            dist = math.sqrt((bx - click[0]) ** 2 + (by - click[1]) ** 2)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    def _is_edge_passing_through(self, edge, node_pos):
        """
        Checks if the given edge passes near the given node position.
        """
        (x1, y1), (x2, y2) = edge  # Unpack edge endpoints
        x, y = node_pos  # Node position

        # Compute perpendicular distance from node to line
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

        return distance < 30  # ✅ Threshold for detecting close proximity (adjustable)


    def _closest_point_on_segment(self, x1, y1, x2, y2, mx, my):
        """
        Finds the closest point on the line segment (x1, y1) -> (x2, y2) to the mouse click (mx, my).
        """
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return x1, y1  # Edge is a point

        # ✅ Compute the projection of (mx, my) onto the edge
        t = ((mx - x1) * dx + (my - y1) * dy) / (dx * dx + dy * dy)

        # ✅ Clamp `t` to the range [0, 1] to ensure it lies on the segment
        t = max(0, min(1, t))

        # ✅ Compute the closest point
        px, py = x1 + t * dx, y1 + t * dy
        return px, py

    def _is_between(self, x1, y1, x2, y2, px, py):
        """
        Checks if the point (px, py) lies between (x1, y1) and (x2, y2).
        """
        return min(x1, x2) - 1 <= px <= max(x1, x2) + 1 and min(y1, y2) - 1 <= py <= max(y1, y2) + 1



    def _update_highlighted_literals(self, literals, clicked_edge=None):
        """
        Updates `self.highlighted_literals` and `self.highlighted_operators` based on user interaction.

        - If a node is clicked → Highlight only that literal.
        - If an edge is clicked:
        - If it's between opposite literals (x, ¬x), highlight both in all corresponding clauses.
        - If it's between different literals (x1, x2), highlight only the `∨` operator between them.
        """
        self.highlighted_literals.clear()  # Reset previous highlights
        self.highlighted_operators.clear()  # Reset highlighted `∨` operators

        if clicked_edge:
            lit1, lit2 = clicked_edge

            # ✅ If the edge is between a literal and its negation, highlight both occurrences
            if lit1[0] == lit2[0] and lit1[1] != lit2[1]:  # Example: (x1, ¬x1)
                var = lit1[0]
                if (var, True) in self.reduction.assignment_mapping and (var, False) in self.reduction.assignment_mapping:
                    u = self.reduction.assignment_mapping[(var, True)]
                    v = self.reduction.assignment_mapping[(var, False)]
                    for node in [u, v]:
                        for (clause_idx, lit_idx), node_id in self.reduction.node_mapping.items():
                            if node_id == node:
                                self.highlighted_literals.add((clause_idx, lit_idx))

            else:
                # ✅ If the edge is between different literals (x1, x2), highlight only the `∨` operator
                for clause_idx, clause in enumerate(self.reduction.formula.clauses):
                    indices = [i for i, lit in enumerate(clause) if lit in [lit1, lit2]]
                    if len(indices) == 2:  # Ensure both literals exist in the same clause
                        self.highlighted_operators.add((clause_idx, min(indices)))

        else: # node clicked
            # ✅ If a node is clicked, highlight **only that literal in all occurrences**
            # for lit in literals:
            #     for (clause_idx, lit_idx), node_id in self.reduction.node_mapping.items():
            #         if self.reduction.graph.nodes[node_id]["literal"] == lit:
            #             self.highlighted_literals.add((clause_idx, lit_idx))
            for lit in literals:
                print(f"Checking literal: {lit}")

                for (clause_idx, lit_idx), node_id in self.reduction.node_mapping.items():
                    node_literal = self.reduction.graph.nodes[node_id].get("literal", None)

                    if node_literal:
                        print(f"Comparing: searched {lit} vs stored {node_literal}")

                    if node_literal == lit:
                        print(f"Match found! Adding (clause_idx: {clause_idx}, lit_idx: {lit_idx}) to highlighted_literals")
                        self.highlighted_literals.add((clause_idx, lit_idx))
                    else:
                        print(f"No match found. Expected {lit} but got {node_literal}")

        print(f"Highlighted literals: {self.highlighted_literals}")
        print(f"Highlighted operators: {self.highlighted_operators}")

   
    def _draw_scene(self):
        """
        Draws the graph, curved edges, and the 3-CNF formula at the top of the screen.
        Highlights selected edges and literals when clicked.
        """
        self.screen.fill((255, 255, 255))  # White background

        # ✅ Draw the 3-CNF Formula at the top of the screen
        self._draw_formula()

        # ✅ Draw edges with curves where necessary
        for u, v in self.graph.edges():
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            # Determine if the edge should be highlighted
            is_highlighted = self.edge_highlight == (u, v) or self.edge_highlight == (v, u)
            edge_color = (255, 0, 0) if is_highlighted else (0, 0, 0)  # Red if clicked, black otherwise

            # Check if edge should be curved (if it passes near another node)
            curve = False
            for node in self.graph.nodes():
                if node != u and node != v:
                    x, y = self.pos[node]
                    if is_edge_passing_through((x1, y1), (x2, y2), (x, y)):
                        curve = True
                        break

            if curve:
                # **Draw curved edge using Bezier curve**
                control_x = (x1 + x2) / 2 + 40  # Offset control point for curve
                control_y = (y1 + y2) / 2 - 40  # Offset to prevent overlap
                draw_curved_edge(self.screen, (x1, y1), (x2, y2), (control_x, control_y), edge_color)
            else:
                # **Draw straight edge**
                pygame.draw.line(self.screen, edge_color, (x1, y1), (x2, y2), 2)

        # ✅ Draw nodes, with highlight effect if connected to selected edge
        self._draw_nodes()

        # ✅ Update display
        pygame.display.flip()
        
 
    def _draw_nodes(self):
        """
        Draws nodes with a different color if they are clicked.
        """
        for node in self.graph.nodes():
            node_color = (255, 150, 0) if self.node_highlight == node else (50, 100, 255)  # Orange if clicked, Blue otherwise
            pygame.draw.circle(self.screen, node_color, self.pos[node], 25)

            lit = self.graph.nodes[node]['literal']
            var_idx, neg, clause_id = lit
            text_label = f"¬x{var_idx}" if neg else f"x{var_idx}"

            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(text_label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.pos[node])
            self.screen.blit(text_surface, text_rect)



    def _draw_formula(self):
        """
        Draws the horizontal 3-CNF formula at the top of the screen with proper brackets.
        - Highlights literals and operators based on user interaction.
        - Ensures `∨` and `∧` are properly spaced and aligned.
        """
        font = pygame.font.SysFont(None, 32, bold=False)  # Use bold for better visibility
        screen_width = self.screen.get_width()

        # ✅ Define starting position
        x_start = 50  # Left margin for rendering formula
        y_position = 30  # Vertical position at the top
        x_offset = x_start  # Tracks current X position

        for c_idx, clause in enumerate(self.formula):
            if c_idx > 0:
                # ✅ Draw AND `∧` between clauses
                and_surface = font.render("AND", True, (0, 0, 0))
                self.screen.blit(and_surface, (x_offset, y_position))
                x_offset += and_surface.get_width() + 15  # Spacing after `∧`

            # ✅ Add opening bracket `(`
            bracket_surface = font.render("(", True, (0, 0, 0))
            self.screen.blit(bracket_surface, (x_offset, y_position))
            x_offset += bracket_surface.get_width() + 5  # Spacing after `(`

            for i, (var, neg, clause_id) in enumerate(clause):  # ✅ Unpack correctly
                literal_text = f"¬x{var}" if neg else f"x{var}"
                color = (255, 0, 0) if (c_idx, i) in self.highlighted_literals else (0, 0, 0)

                # ✅ Render the literal text with highlighting
                text_surface = font.render(literal_text, True, color)
                self.screen.blit(text_surface, (x_offset, y_position))
                x_offset += text_surface.get_width() + 10  # Move X position forward

                if i < len(clause) - 1:
                    # ✅ Draw OR `∨` operator
                    or_color = (255, 0, 0) if c_idx in self.highlighted_operators else (0, 0, 0)
                    or_surface = font.render("OR", True, or_color)
                    self.screen.blit(or_surface, (x_offset, y_position))
                    x_offset += or_surface.get_width() + 10  # Spacing after `∨`

            # ✅ Add closing bracket `)`
            bracket_surface = font.render(")", True, (0, 0, 0))
            self.screen.blit(bracket_surface, (x_offset, y_position))
            x_offset += bracket_surface.get_width() + 15 

    def show_mapping(self, sat_assignment):
        self.run()
        """
        Visualizes the solution mapping:
        - Evaluates the SAT formula with the given assignments.
        - Highlights nodes corresponding to literals that evaluate to 1.
        - Updates the formula display with values.

        Args:
            sat_assignment: Dictionary mapping variables to their truth values (0/1).
        """
        # Convert SAT assignment to an Independent Set
        independent_set = self.reduction.sol1tosol2(sat_assignment)

        # Replace variables in the formula with their assigned values
        formula_with_values = []
        for clause in self.formula:
            new_clause = []
            for var, is_negated, _ in clause:
                assigned_value = sat_assignment.get(var, None)
                if assigned_value is None:
                    new_clause.append(f"x{var}")  # Keep variable if missing from assignment
                else:
                    value = int(not assigned_value) if is_negated else int(assigned_value)  # Handle negation
                    new_clause.append(str(value))

            formula_with_values.append(f"({' ∨ '.join(new_clause)})")

        formula_text = " ∧ ".join(formula_with_values)

        # Print the formula with values for debugging
        print(f"Formula with Assigned Values: {formula_text}")
        print(f"Independent Set Nodes: {independent_set}")

        # Highlight the nodes in the graph
        self.highlighted_nodes = independent_set
        independent_literals = self.reduction.sol1tosol2(sat_assignment)
        # Refresh the visualization to display the updated formula and highlighted nodes
        self._update_highlighted_literals(independent_literals)

    def update_display(self, formula_text):
        """
        Updates the PyGame visualization by:
        - Redrawing the formula with assigned truth values.
        - Highlighting nodes in the independent set.
        """
        self.formula = formula_text  # Store the modified formula for display
        self.draw_solution_mapping(formula_text)  # Redraw the visualization

    def draw_solution_mapping(self, formula_text):
        """
        Draws the SAT formula with assigned truth values at the top of the screen.
        Highlights the selected nodes that form the independent set.

        Args:
            formula_text (str): The formatted formula with assigned values.
        """
        self.screen.fill(BACKGROUND_COLOR)  # Clear screen

        # ✅ Draw updated formula at the top
        font = pygame.font.SysFont(None, 32, bold=False)
        text_surface = font.render(formula_text, True, (0, 0, 0))  # Black text
        self.screen.blit(text_surface, (50, 30))  # Draw formula at the top

        # ✅ Draw edges (unaffected)
        for u, v in self.graph.edges():
            pygame.draw.line(self.screen, EDGE_COLOR, self.pos[u], self.pos[v], 2)

        # ✅ Draw nodes with highlighting if in independent_set
        for node in self.graph.nodes():
            node_color = HIGHLIGHT_NODE_COLOR if node in self.highlighted_nodes else NODE_COLOR
            pygame.draw.circle(self.screen, node_color, self.pos[node], RADIUS)

            # Draw text inside node
            font = pygame.font.SysFont(None, 24)
            text_label = str(node)
            text_surface = font.render(text_label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.pos[node])
            self.screen.blit(text_surface, text_rect)

        # ✅ Refresh screen
        pygame.display.flip()

def draw_curved_edge(screen, start, end, control, color):
    """
    Draws a quadratic Bezier curve between two points using a control point.
    """
    points = []
    for t in range(0, 21):  # Generate 20 points along the curve
        t /= 20.0
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1]
        points.append((int(x), int(y)))

    pygame.draw.lines(screen, color, False, points, 2)  # Draw curved line


def is_edge_passing_through(start, end, node_pos):
    """
    Checks if an edge between (start, end) passes near node_pos.
    """
    x1, y1 = start
    x2, y2 = end
    x, y = node_pos

    # Compute the perpendicular distance from node to line
    distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

    return distance < 30  # Adjust threshold as needed


