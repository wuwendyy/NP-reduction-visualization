import math
import pygame
import numpy as np
import networkx as nx
from abc import abstractmethod
from npvis.element.graph.node import Node
from npvis.element.graph.edge import Edge
from npvis.element.graph.graph_drawing_utils import (
    has_overlapping_edge,
    draw_bezier_curve,
    draw_thick_bezier_curve,
    find_best_control_point
)

class Graph:
    name_dict = dict()  # stores name: node
    groups = []
    '''
    Inputs: 
    nodes: set of Nodes
    edges: set of Edges as nodes
    groups: list of list of node as groups. If it is not empty, assumes all nodes has group assignments 
    bounding box: 2*2 matrix of [x_min, y_min],[x_max, y_max]
    node radius: radius of (most) nodes 
    '''

    def __init__(self, nodes=set(), edges=set(), groups=[], bounding_box=np.array([[50, 50], [550, 550]]),
                 node_radius=20):
        self.nodes = nodes
        self.edges = edges
        self.groups = groups
        self.bounding_box = bounding_box
        self.original_bounding_box = bounding_box
        self.node_dict = None
        self._create_node_dictionary()
        self.node_radius = node_radius

    def set_bounding_box(self, bounding_box):
        """
        Sets the bounding box for the graph. Adjusts the given bounding box
        by the node_radius so that when nodes are placed (by their center),
        the entire node (circle) remains visible.
        
        Args:
            bounding_box (np.array): 2x2 array of form [[x_min, y_min], [x_max, y_max]]
        """
        margin = self.node_radius
        # Adjust bounding box so that node centers are confined within an area that
        # leaves a margin of 'node_radius' on all sides.
        adjusted_box = np.array([
            [bounding_box[0][0] + margin, bounding_box[0][1] + margin],
            [bounding_box[1][0] - margin, bounding_box[1][1] - margin]
        ])
        self.bounding_box = adjusted_box
        self.original_bounding_box = bounding_box

    def print_display(self):
        print("Nodes:")
        for node in self.nodes:
            print(f"{node.node_id}, ", end="")
        print("\nEdges:")
        for edge in self.edges:
            print(f"({edge.node1.node_id}, {edge.node2.node_id}), ", end="")
        print("\nGroups:")
        for group in self.groups:
            for node in group:
                print(f"{node.node_id}, ", end="")
            print()

    def parse(self, filename):
        '''
        Read in nodes, edges, and groups from a file
        '''
        self.nodes = []  # Ensure fresh
        self.edges = []
        self.groups = []
        with open(filename, "r") as file:
            counter = 0
            for line in file:
                line = line.strip()
                if line[0] == '(':  # edge
                    names = line[1:-1].split(", ")
                    node1 = self.name_dict.get(names[0])
                    node2 = self.name_dict.get(names[1])
                    e = Edge(node1, node2)
                    self.edges.append(e)
                    node1.add_neighbor(node2.node_id)
                    node2.add_neighbor(node1.node_id)
                elif line[0] == '[':  # group
                    names = line[1:-1].split(", ")
                    group = []
                    for name in names:
                        group.append(self.name_dict.get(name))
                    self.groups.append(group)
                else:  # node
                    n = Node(counter, line)
                    counter += 1
                    self.nodes.append(n)
                    self.name_dict[line] = n

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, edge):
        self.edges.add(edge)
        
    def hasEdge(self, node1, node2):
        return any(
            (edge.node1 == node1 and edge.node2 == node2) or
            (edge.node1 == node2 and edge.node2 == node1)
            for edge in self.edges
        )

    def get_node_by_id(self, node_id):
        """
        Retrieve a node from the graph using its node_id.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            Node object if found, else None.
        """
        return next((node for node in self.nodes if node.node_id == node_id), None)

    def determine_node_positions(self):
        if len(self.groups) != 0:
            # has group assignment 
            self.determine_node_positions_by_groups()
        else:
            # use networkx to generate node positions
            self.determine_node_positions_nx()
        return

    def _create_node_dictionary(self):
        self.node_dict = {node.node_id: node for node in self.nodes}

    def _rotate_vector_np(self, vector, angle_degrees):
        angle_radians = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians),  np.cos(angle_radians)]
        ])
        return rotation_matrix @ vector

    def determine_node_positions_by_groups(self, group_size=200, gap=40):
        group_num = len(self.groups)
        groups_per_row = max(math.ceil(math.sqrt(group_num)), 4)
        groups_per_col = math.ceil(group_num / groups_per_row)
        bounding_box_dim = self.bounding_box[1, :] - self.bounding_box[0, :]
        width_per_groups = min((bounding_box_dim[0] / groups_per_row), (bounding_box_dim[1] / groups_per_col))
        width_per_groups = min(width_per_groups, group_size)
        radius = width_per_groups / 2.
        r = 0
        c = 0
        start_vector = np.array([0, -1. * radius])
        for group in self.groups:
            center = np.array([gap * c, gap * r]) + self.bounding_box[0, :] + np.array(
                [(0.5 + c) * width_per_groups, (0.5 + r) * width_per_groups]
            )
            angle = 360. / len(group)
            for i in range(len(group)):
                displacement = self._rotate_vector_np(start_vector, i * angle)
                node_new_pos = center + displacement
                group[i].location = node_new_pos
            c += 1
            if c == groups_per_row:
                r += 1
                c = 0

    def determine_node_positions_nx(self):
        g = nx.Graph()
        g.add_nodes_from(self.node_dict.keys())
        for edge in self.edges:
            g.add_edge(edge.node1.node_id, edge.node2.node_id)
        node_pos = nx.arf_layout(g)
        bounding_box_dim = self.bounding_box[1, :] - self.bounding_box[0, :]
        bounding_box_center = 0.5 * (self.bounding_box[0] + self.bounding_box[1])
        node_pos = nx.rescale_layout_dict(node_pos, 1)
        for node in self.nodes:
            node.location = node_pos[node.node_id] * (bounding_box_dim / 2)
            node.location = np.add(node.location, bounding_box_center)

    def display(self, screen):
        # Draw edges
        for edge in self.edges:
            start_pos = edge.node1.location
            end_pos = edge.node2.location
            if has_overlapping_edge(edge, self.nodes, self.node_radius):
                control_point = find_best_control_point(start_pos, end_pos, self.nodes, self.node_radius)
                draw_thick_bezier_curve(screen, start_pos, control_point, end_pos, edge.color, width=1)
            else:
                pygame.draw.line(screen, edge.color, start_pos.astype(int), end_pos.astype(int), 3)
        
        # Draw nodes
        for node in self.nodes:
            pygame.draw.circle(screen, node.color, node.location.astype(int), self.node_radius)
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(node.name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(int(node.location[0]), int(node.location[1])))
            screen.blit(text_surface, text_rect)
            
        # Debug bounding box
        pygame.draw.rect(
            screen,
            (0, 0, 255),
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
            pos = np.array(event.pos)
            # Check each node to see if the click falls within the node's circle.
            for node in self.nodes:
                if is_inside_circle(pos, node.location, self.node_radius):
                    node.change_color((255, 0, 0))  # Change color to red when clicked
                    print(f"Node {node.node_id} ({node.name}) was clicked at {event.pos}.")
                    # You can add more logic here, such as highlighting or callbacks.

# Function to detect if a point is inside a circle
def is_inside_circle(point, circle_center, radius):
    return np.linalg.norm(point - circle_center) <= radius
