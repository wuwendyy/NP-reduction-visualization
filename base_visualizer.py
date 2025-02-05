import pygame
import networkx as nx

# Basic PyGame / drawing constants
WIDTH, HEIGHT = 800, 600
# Colors for visualization
BACKGROUND_COLOR = (255, 255, 255)  # White background
NODE_COLOR = (34,139,34)  # Blue nodes (adjust as needed)
EDGE_COLOR = (0, 0, 0)  # Black edges
LABEL_COLOR = (0, 0, 0)  # Black text for visibility
HIGHLIGHT_NODE_COLOR = (255, 100, 100)  # Red highlight for selected nodes

RADIUS = 20

class BaseGraphVisualizer:
    """
    A base PyGame + NetworkX visualizer that can be extended for
    specialized NP reductions or 3-SAT layouts.
    """

    def __init__(self, graph=None, width=WIDTH, height=HEIGHT):
        """
        Args:
            graph: A NetworkX graph object.
            width, height: Screen dimensions for PyGame window.
        """
        self.graph = graph if graph is not None else nx.Graph()
        self.width = width
        self.height = height

        # PyGame setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Base Graph Visualizer")
        self.clock = pygame.time.Clock()
        self.running = False

        # For storing layout positions: {node: (x, y)}
        self.pos = {}

        # Basic interaction
        self.highlighted_nodes = set()

    def run(self, fps=30):
        """
        Main PyGame loop.
        """
        self._compute_layout()  # Let subclass define or override
        self.running = True

        while self.running:
            self._handle_events()
            self._draw_scene()
            pygame.display.flip()
            self.clock.tick(fps)

        pygame.quit()

    def _compute_layout(self):
        """
        Compute node positions based on the selected layout.
        """
        if self.layout_mode == 'force':
            self.pos = nx.spring_layout(self.graph, iterations=50)
            self.pos = nx.rescale_layout_dict(self.pos, scale=1.0)

        elif self.layout_mode == '3sat_triangles':
            self.pos = self._layout_3sat_clauses(
                formula=self.formula, clause_vertices=self.clause_vertices,
                start_x=150, start_y=300, x_gap=250, radius=80
            )

        # ✅ Debug: Print node positions
        print("Node positions:", self.pos)


    def _draw_scene(self):
        """
        Draws the entire graph, including nodes and edges.
        """
        self.screen.fill(BACKGROUND_COLOR)  # White background

        # **Ensure edges are drawn**
        for u, v in self.graph.edges():
            sx1, sy1 = self._scale_position(self.pos[u])
            sx2, sy2 = self._scale_position(self.pos[v])
            pygame.draw.line(self.screen, EDGE_COLOR, (sx1, sy1), (sx2, sy2), 2)  # Black edges

        # Draw nodes
        for node in self.graph.nodes():
            self._draw_node(node)


    def _draw_node(self, node):
        """
        Draws a node with different colors if highlighted.
        """
        sx, sy = self._scale_position(self.pos[node])

        # **Change color if node is highlighted**
        color = HIGHLIGHT_NODE_COLOR if node in self.highlighted_nodes else NODE_COLOR

        pygame.draw.circle(self.screen, color, (int(sx), int(sy)), RADIUS)

        # Draw node label (e.g., x1, ¬x2)
        data = self.graph.nodes[node]
        if 'literal' in data:
            var_idx, neg = data['literal']
            text_label = f"¬x{var_idx}" if neg else f"x{var_idx}"
        else:
            text_label = str(node)

        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(text_label, True, LABEL_COLOR)
        text_rect = text_surface.get_rect(center=(sx, sy))
        self.screen.blit(text_surface, text_rect)


    def _scale_position(self, xy):
        """
        Convert graph layout positions (from [0,1] range) to screen coordinates.
        """
        x, y = xy

        # Adjust scaling based on layout type
        if self.layout_mode == 'force':
            sx = int((x * 0.8 + 0.1) * self.width)  # Scale from [0,1] to screen width
            sy = int((y * 0.8 + 0.1) * self.height)
        elif self.layout_mode == '3sat_triangles':
            # If the layout already uses pixel coordinates, return as-is
            sx = int(x)
            sy = int(y)
        else:
            sx = int(x * self.width)
            sy = int(y * self.height)

        return (sx, sy)


    def _handle_events(self):
        """
        Subclass can extend or override. Default: handle QUIT, highlight on clicks, etc.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                # Press 'q' to quit
                if event.key == pygame.K_q:
                    self.running = False

    def _handle_mouse_click(self, mouse_pos):
        """
        Detect if a user clicks on a node and toggle highlight.
        """
        mx, my = mouse_pos
        for node, p in self.pos.items():
            sx, sy = self._scale_position(p)
            dist_sq = (sx - mx)**2 + (sy - my)**2  # Check if click is within node radius
            if dist_sq <= RADIUS**2:
                if node in self.highlighted_nodes:
                    self.highlighted_nodes.remove(node)  # Remove highlight
                else:
                    self.highlighted_nodes.add(node)  # Highlight node
                break  # Exit after first match
