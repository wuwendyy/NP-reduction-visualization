import pygame
import numpy as np
from elements import Graph, Formula, Edge, Node

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Graph and Formula Display")
clock = pygame.time.Clock()

# Define bounding boxes for both elements
graph_bounding_box = np.array([[400, 50], [780, 550]])  # Right side of the window
formula_bounding_box = np.array([[20, 50], [380, 200]])  # Left upper side

# Initialize graph with nodes, edges, and groups
nodes = set()
node_count = 9
node_list = []
for i in range(node_count):
    node = Node(node_id=i, name=f"{i}")
    nodes.add(node)
    node_list.append(node)

edges = set()
groups = []
group_size = 3

for i in range(0, node_count, group_size):
    group = node_list[i:i + group_size]
    if len(group) == group_size:
        groups.append(group)
        for a in range(group_size):
            for b in range(a + 1, group_size):
                edges.add(Edge(group[a], group[b]))

# Create graph and determine node positions
graph = Graph(nodes=nodes, edges=edges, groups=groups, bounding_box=graph_bounding_box, node_radius=20)
graph.determine_node_positions_by_groups()

# Initialize formula and parse from file
formula = Formula(formula_bounding_box)
formula.parse("sample_elements/sampleFormula.txt")  # Provide correct file path

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Display both elements
    graph.display(screen)
    formula.display(screen)

    pygame.display.flip()
    clock.tick(30)  # Limit FPS to 30

pygame.quit()
