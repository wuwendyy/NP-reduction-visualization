import math
import pygame
import numpy as np

from abc import abstractmethod
from npvis.element.helpers import Node, Edge, Clause, Variable
from npvis.element.graph_drawing_utils import (
    has_overlapping_edge, 
    draw_bezier_curve,
    draw_thick_bezier_curve, 
    find_best_control_point
)

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
        self._create_node_dictionary()
        self.node_radius = node_radius
        
    def set_bounding_box(self, bounding_box):
        self.bounding_box = bounding_box

    # placeholder print display
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
        
    def hasEdge(self, node1, node2):
        return any(edge.node1 == node1 and edge.node2 == node2 or edge.node1 == node2 and edge.node2 == node1 for edge in self.edges)

    def get_node_by_id(self, node_id):
        """
        Retrieve a node from the graph using its node_id.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            Node object if found, else None.
        """
        return next((node for node in self.nodes if node.node_id == node_id), None)

    '''
    Helper function in determine the node positions 
    '''

    def determine_node_positions(self):
        if len(self.groups) != 0:
            # has group assignment 
            self.determine_node_positions_by_groups()
        return
    
    def _create_node_dictionary(self):
        '''
        Create dictionary for node loop up
        '''
        self.node_dict = {node.node_id: node for node in self.nodes}

    def _rotate_vector_np(self, vector, angle_degrees):
        '''
        Helper function for 2d vector rotations  
        '''
        angle_radians = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians), np.cos(angle_radians)]
        ])
        return rotation_matrix @ vector

    # def get_node_by_id(self, id):
    #     '''
    #     Helper function to get node by id 
    #     '''
    #     return self.node_dict.get(id)

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
                displacement = self._rotate_vector_np(start_vector, i * angle)
                node_new_pos = center + displacement
                group[i].location = node_new_pos

            c += 1
            if c == groups_per_row:
                r += 1
                c = 0

    def display(self, screen):
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

class Formula:
    def __init__(self, bounding_box=np.array([[50, 50], [550, 550]])):
        self.clauses = []
        self.bounding_box = bounding_box
        self.font = None
        self.literal_dict = {}
        
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
                    is_not_negated = True
                    if tokens[i] == "NOT":
                        is_not_negated = False
                        i += 1  # Move to variable name

                    var_name = tokens[i]
                    variable = Variable(var_name, is_not_negated, counter, variable_counter)
                    variable_counter += 1
                    clause.add_variable(variable)

                    i += 2  # Skip OR

                self.clauses.append(clause)

    def get_as_list(self):
        return [[v for v in clause.variables] for clause in self.clauses]

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

        # Convert clauses into formatted strings
        formatted_clauses = []
        for clause in self.clauses:
            clause_str = "(" + " OR ".join(str(var) for var in clause.variables) + ")"
            formatted_clauses.append(clause_str)

        text_lines = []
        current_line = ""

        for clause in formatted_clauses:
            temp_surface = self.font.render(current_line + (" AND " if current_line else "") + clause, True, (0, 0, 0))
            temp_width = temp_surface.get_width()

            if temp_width > max_width:
                if not current_line:
                    raise ValueError(f"Clause '{clause}' is too wide to fit in bounding box.")

                text_lines.append(current_line)
                current_line = clause
            else:
                current_line += (" AND " if current_line else "") + clause

        if current_line:
            text_lines.append(current_line)

        if len(text_lines) * line_height > max_height:
            raise ValueError("Not enough space to display all clauses within the bounding box.")

        for i, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (x, current_y + i * line_height))
    