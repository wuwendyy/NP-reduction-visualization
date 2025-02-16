from abc import abstractmethod
from helpers import *
import numpy as np
import math
import pygame


class Element:
    # display to pygame
    @abstractmethod
    def display(self):
        pass

    # parse in from file
    @abstractmethod
    def parse(self):
        pass


class Graph(Element):
    '''
    Inputs: 
    nodes: set of Nodes
    esges: set of Edges as nodes 
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
    # def display(self):
    #     print("Nodes:")
    #     for node in self.nodes:
    #         print(node.node_id)
    #     print("Edges:")
    #     for edge in self.edges:
    #         print(f"( {edge.node1.node_id}, {edge.node2.node_id})")

    def parse(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                pass

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


# Example Formula
"""
formula.clauses = [ #(var, is_negated, clause_idx)
    [(1, False, 1), (2, True, 1), (3, False, 1)],
    [(2, False, 2), (3, True, 2), (4, False, 2)],
    [(1, False, 3), (2, True, 3), (4, False, 3)]
]
"""


class Formula(Element):
    clauses = []

    def parse(self, filename):
        counter = 0
        with open(filename, "r") as f:
            x = f.read().split("OR")
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
        f.close()
        print(self.clauses)

# return as a list of list of tuples
    def get_as_list(self):
        outer_list = []
        for clause in self.clauses:
            inner_list = []
            for var in clause.variables:
                tup = (var.var_id, var.negate, clause.clause_id)
                inner_list.append(tup)
            outer_list.append(inner_list)
        return outer_list

    def evaluate(self):
        for c in self.clauses:
            pass

    def display(self):
        pass
