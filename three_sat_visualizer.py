import math
import pygame
import networkx as nx

from base_visualizer import BaseGraphVisualizer, WIDTH, HEIGHT, BACKGROUND_COLOR, \
                           NODE_COLOR, EDGE_COLOR, HIGHLIGHT_NODE_COLOR, LABEL_COLOR, RADIUS

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
    def __init__(self, graph, clause_vertices, formula, literal_to_formula_indices, width=1000, height=700):
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

        # Initialize PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3-SAT Graph Visualizer")
        self.clock = pygame.time.Clock()

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
        Handle mouse click to select edges.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_edge_click(pygame.mouse.get_pos())

    def _handle_edge_click(self, mouse_pos):
        """
        Detect if a user clicks on an edge and highlight corresponding literals in the formula.
        """
        mx, my = mouse_pos
        self.edge_highlight = None  # Reset highlight if no edge is clicked

        for u, v in self.graph.edges():
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            # Check if click is near the edge using point-line distance formula
            distance = abs((y2 - y1) * mx - (x2 - x1) * my + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
            
            if distance < 10:  # If close enough to the edge, select it
                self.edge_highlight = (u, v)
                break  # Stop checking other edges


    def _draw_scene(self):
        """
        Draws the graph and highlights the selected edge's literals in the formula.
        """
        self.screen.fill((255, 255, 255))  # White background

        # Draw edges
        for u, v in self.graph.edges():
            color = (255, 0, 0) if self.edge_highlight == (u, v) or self.edge_highlight == (v, u) else (0, 0, 0)
            pygame.draw.line(self.screen, color, self.pos[u], self.pos[v], 2)

        # Draw nodes
        for node in self.graph.nodes():
            pygame.draw.circle(self.screen, (50, 100, 255), self.pos[node], 25)
            lit = self.graph.nodes[node]['literal']
            var_idx, neg = lit
            text_label = f"¬x{var_idx}" if neg else f"x{var_idx}"

            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(text_label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.pos[node])
            self.screen.blit(text_surface, text_rect)

        # ✅ Draw formula with highlight only when an edge is clicked
        font = pygame.font.SysFont(None, 32)
        highlighted_literals = set()

        if self.edge_highlight:
            u, v = self.edge_highlight
            lit1 = self.graph.nodes[u]["literal"]
            lit2 = self.graph.nodes[v]["literal"]

            if lit1 in self.literal_to_formula_indices:
                highlighted_literals.update(self.literal_to_formula_indices[lit1])
            if lit2 in self.literal_to_formula_indices:
                highlighted_literals.update(self.literal_to_formula_indices[lit2])

        for c_idx, clause in enumerate(self.formula):
            clause_text = " ∨ ".join([f"¬x{v}" if n else f"x{v}" for v, n in clause])
            color = (255, 0, 0) if any((c_idx, i) in highlighted_literals for i in range(len(clause))) else (0, 0, 0)
            text_surface = font.render(f"({clause_text})", True, color)
            self.screen.blit(text_surface, (20, 20 + c_idx * 40))
