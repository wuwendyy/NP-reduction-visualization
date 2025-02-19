import numpy as np
import math
import pygame

from abc import abstractmethod
from helpers import *


class Element:
    # display to pygame
    @abstractmethod
    def display(self):
        raise NotImplementedError

    # parse in from file
    @abstractmethod
    def parse(self, filename):
        raise NotImplementedError


class Graph(Element):
    name_dict = dict()  # stores name:node
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
        self.node_dict = None
        self.create_node_dictionary()
        self.node_radius = node_radius

    # placeholder print display
    # def print_display(self):
    #     print("Nodes:")
    #     for node in self.nodes:
    #         print(node.node_id)
    #     print("Edges:")
    #     for edge in self.edges:
    #         print(f"({edge.node1.node_id}, {edge.node2.node_id})")
    #     print("Groups:")
    #     for group in self.groups:
    #         for node in group:
    #             print(f"{node.node_id}, ", end="")
    #         print()

    '''
    Read in nodes, edges, and groups from a file
    '''
    def parse(self, filename):
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
                    self.name_dict[line] = n  # append to node_dict for future lookup

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, edge):
        self.edges.add(edge)

    '''
    Helper function in determine the node positions 
    '''

    def determine_node_positions(self):
        if len(self.groups) != 0:
            # has group assignment 
            self.determine_node_positions_by_groups()
        return

    '''
    Helper function for 2d vector rotations  
    '''

    def rotate_vector_np(self, vector, angle_degrees):
        angle_radians = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians), np.cos(angle_radians)]
        ])
        return rotation_matrix @ vector

    '''
    Helper function to get node by id 
    '''

    def get_node_by_id(self, id):
        return self.node_dict.get(id)

    '''
    Create dictionary for node loop up
    '''

    def create_node_dictionary(self):
        self.node_dict = {node.node_id: node for node in self.nodes}

    def determine_node_positions_by_groups(self, group_size=200, gap=40):
        # assign group areas
        # TODO: count in gaps in distributing the bounded space 
        group_num = len(self.groups)
        groups_per_row = max(math.ceil(math.sqrt(group_num)), 4)
        groups_per_col = math.ceil(group_num / groups_per_row)

        bounding_box_dim = self.bounding_box[1, :] - self.bounding_box[0, :]
        width_per_groups = min((bounding_box_dim[0] / groups_per_row), (bounding_box_dim[1] / groups_per_col))
        width_per_groups = min(width_per_groups, group_size)
        radius = width_per_groups / 2.
        # loop through each groups 
        r = 0
        c = 0
        start_vector = np.array([0, -1. * radius])
        for group in self.groups:
            center = np.array([gap * c, gap * r]) + self.bounding_box[0, :] + np.array(
                [(0.5 + c) * width_per_groups, (0.5 + r) * width_per_groups])
            angle = 360. / len(group)
            for i in range(len(group)):
                displacement = self.rotate_vector_np(start_vector, i * angle)
                node_new_pos = center + displacement
                group[i].location = node_new_pos

            c += 1
            if c == groups_per_row:
                r += 1
                c = 0

    def display(self, screen):
        # Draw edges
        for edge in self.edges:
            start_pos = edge.node1.location
            end_pos = edge.node2.location
            pygame.draw.line(screen, edge.color, start_pos, end_pos, 3)

        # Draw nodes
        for node in self.nodes:
            pygame.draw.circle(screen, node.color, node.location.astype(int), self.node_radius)
            # Optionally draw node name in the center
            font = pygame.font.SysFont(None, 24)
            text_surface = font.render(node.name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(int(node.location[0]), int(node.location[1])))
            screen.blit(text_surface, text_rect)


class Formula:
    def __init__(self, bounding_box=np.array([[50, 50], [550, 550]])):
        self.clauses = []
        self.bounding_box = bounding_box
        self.font = None

    def parse(self, filename):
        self.clauses = []  # Ensure fresh parsing each time
        counter = 0
        with open(filename, "r") as f:
            x = f.read().split("AND")
            for c in x:
                counter += 1
                c = c.strip()[1:-1]  # remove the parentheses
                clause = Clause(counter)
                v = c.split()
                i = 0
                while i < len(v):
                    negate = False
                    if v[i] == "NOT":
                        negate = True
                        i += 1
                    var = Variable(v[i], negate)
                    clause.add_variable(var)
                    i += 2  # skip the AND part
                self.clauses.append(clause)

    """
    Return a list of list of tuples
    formula.clauses = [ #(var, is_negated, clause_idx)
        [('X1', False, 1), ('X2', True, 1), ('X3', False, 1)],
        [('X2', False, 2), ('X3', True, 2), ('X4', False, 2)],
        [('X1', False, 3), ('X2', True, 3), ('X4', False, 3)]
    ]
    """

    def get_as_list(self):
        outer_list = []
        for clause in self.clauses:
            inner_list = []
            for var in clause.variables:
                tup = (var.var_id, var.negate, clause.clause_id)
                inner_list.append(tup)
            outer_list.append(inner_list)
        return outer_list

    def evaluate(self, solution: SATSolution):
        return all(c.evaluate(solution) for c in self.clauses)

    def display(self, screen):
        if self.font is None:
            self.font = pygame.font.SysFont(None, 24)

        x, y = self.bounding_box[0]
        max_width = self.bounding_box[1][0] - x
        max_height = self.bounding_box[1][1] - y
        line_height = 30  # Height of each line of text
        current_x, current_y = x, y

        clauses = self.get_as_list()
        formatted_clauses = ["(" + " OR ".join([f"{'¬' if neg else ''}{var}" for var, neg, _ in clause]) + ")" for
                             clause in clauses]

        text_lines = []
        current_line = ""

        for clause in formatted_clauses:
            temp_surface = self.font.render(current_line + (" AND " if current_line else "") + clause, True, (0, 0, 0))
            temp_width = temp_surface.get_width()

            # If adding this clause exceeds the bounding box width
            if temp_width > max_width:
                if not current_line:  # If the clause alone is too wide, raise an error
                    raise ValueError(f"Clause '{clause}' is too wide to fit within the bounding box.")

                text_lines.append(current_line)  # Store the current line
                current_line = clause  # Start a new line with the clause
            else:
                if current_line:
                    current_line += " AND " + clause
                else:
                    current_line = clause

        if current_line:  # Append the last line if any remaining text
            text_lines.append(current_line)

        # Check if text fits within bounding box height
        if len(text_lines) * line_height > max_height:
            raise ValueError("Not enough space to display all clauses within the bounding box.")

        # Render and blit each line
        for i, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (x, y + i * line_height))
