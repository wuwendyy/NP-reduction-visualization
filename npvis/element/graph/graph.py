import math
import pygame
import numpy as np
import networkx as nx

from abc import abstractmethod
from npvis.element.graph.node import Node
from npvis.element.graph.edge import Edge
from npvis.element.element import Element
from npvis.element.graph.graph_drawing_utils import (
    has_overlapping_edge,
    draw_bezier_curve,
    draw_thick_bezier_curve,
    find_best_control_point,
    is_inside_circle
)
from npvis.element.color import LIGHTGREY
from npvis.const import DATA_DIR
from pathlib import Path

class Graph(Element):
    """
    A Graph with optional grouping.  When `groups` is nonempty,
    `determine_node_positions()` splits the bounding box into a grid
    of one cell per group (plus one extra cell for any ungrouped nodes)
    and lays out each cell’s nodes in a neat circle.
    """
    def __init__(self,
                 nodes=set(),
                 edges=set(),
                 groups=None,
                 bounding_box=np.array([[50,50],[550,550]]),
                 node_radius=20):
        self.nodes = set(nodes)
        self.edges = set(edges)
        self.groups = list(groups) if groups is not None else []
        self.original_bounding_box = np.array(bounding_box, dtype=float)
        self.node_radius = node_radius

        # inset bounding_box so that node *centers* never exceed the drawable area
        margin = self.node_radius + 5
        x0,y0 = self.original_bounding_box[0]
        x1,y1 = self.original_bounding_box[1]
        self.bounding_box = np.array([
            [x0 + margin, y0 + margin],
            [x1 - margin, y1 - margin]
        ], dtype=float)

        self._create_node_dictionary()

    def _create_node_dictionary(self):
        self.node_dict = {node.id: node for node in self.nodes}

    def add_node(self, node: Node):
        self.nodes.add(node)
        self._create_node_dictionary()

    def add_edge(self, edge: Edge):
        self.edges.add(edge)

    def add_group(self, nodes: [Node]): # type: ignore
        # TODO
        pass

    def hasEdge(self, n1, n2):
        return any((e.node1==n1 and e.node2==n2) or (e.node1==n2 and e.node2==n1)
                   for e in self.edges)

    def get_node_by_id(self, node_id):
        return self.node_dict.get(node_id)

    def set_bounding_box(self, bounding_box):
        """
        Reset the outer bounding box (and re‑inset it).
        """
        self.original_bounding_box = np.array(bounding_box, dtype=float)
        margin = self.node_radius + 5
        x0,y0 = self.original_bounding_box[0]
        x1,y1 = self.original_bounding_box[1]
        self.bounding_box = np.array([
            [x0 + margin, y0 + margin],
            [x1 - margin, y1 - margin]
        ], dtype=float)

    def determine_node_positions(self):
        if self.groups:
            self._determine_node_positions_grouped()
        else:
            self._determine_node_positions_nx()

    def _determine_node_positions_grouped(self):
        """
        Split bounding_box into N+1 cells (N = len(groups)):
          - first N cells for the N groups
          - final cell for any leftover nodes
        Lay out each cell’s nodes in a circle.
        """
        all_grouped = {n for group in self.groups for n in group}
        leftovers = [n for n in self.nodes if n not in all_grouped]

        # build a list of “cells” = one per group, plus one for leftovers
        cells = self.groups.copy()
        if leftovers:
            cells.append(leftovers)

        G = len(cells)
        cols = math.ceil(math.sqrt(G))
        rows = math.ceil(G / cols)

        # overall dims
        (x0,y0), (x1,y1) = self.bounding_box
        w = x1 - x0
        h = y1 - y0
        cell_w = w / cols
        cell_h = h / rows

        def cell_bbox(idx):
            r = idx // cols
            c = idx % cols
            cx0 = x0 + c * cell_w
            cy0 = y0 + r * cell_h
            return np.array([[cx0,    cy0],
                             [cx0+cell_w, cy0+cell_h]])

        for idx, group in enumerate(cells):
            box = cell_bbox(idx)
            center = (box[0] + box[1]) / 2
            radius = min(cell_w, cell_h)/2 - self.node_radius - 5
            if radius < 0:
                radius = min(cell_w, cell_h)/2 * 0.4  # fallback fraction
            
            max_radius = self.node_radius + 20
            if radius > max_radius:
                radius = max_radius

            N = len(group)
            for i,node in enumerate(group):
                angle = 2*math.pi * i / N
                offset = np.array([math.cos(angle), math.sin(angle)]) * radius
                node.location = center + offset

    def _determine_node_positions_nx(self):
        """
        Place ALL nodes via NetworkX’s ARF layout if there are no groups.
        """
        g = nx.Graph()
        for n in self.nodes:
            g.add_node(n.id)
        for e in self.edges:
            g.add_edge(e.node1.id, e.node2.id)

        pos = nx.arf_layout(g)
        pos = nx.rescale_layout_dict(pos, 1.0)

        (x0,y0),(x1,y1) = self.bounding_box
        center = ((x0+x1)/2, (y0+y1)/2)
        scale_x = (x1 - x0)/2
        scale_y = (y1 - y0)/2

        for n in self.nodes:
            px,py = pos[n.id]
            n.location = np.array([center[0] + px*scale_x,
                                   center[1] + py*scale_y])

    def display(self, screen):
        # edges
        for e in self.edges:
            a = e.node1.location
            b = e.node2.location
            if has_overlapping_edge(e, self.nodes, self.node_radius):
                cp = find_best_control_point(a,b,self.nodes,self.node_radius)
                draw_thick_bezier_curve(screen, a, cp, b, e.color, width=3)
            else:
                pygame.draw.line(screen, e.color, a.astype(int), b.astype(int), 3)

        # nodes
        for n in self.nodes:
            pygame.draw.circle(screen, n.color,
                               n.location.astype(int),
                               self.node_radius)
            font = pygame.font.SysFont(None, 24)
            surf = font.render(str(n.name), True, (255,255,255))
            rect = surf.get_rect(center=n.location.astype(int))
            screen.blit(surf, rect)

        # debug: outer bbox
        x0,y0 = self.original_bounding_box[0]
        x1,y1 = self.original_bounding_box[1]
        pygame.draw.rect(screen, LIGHTGREY,
                         pygame.Rect(x0, y0, x1-x0, y1-y0),
                         width=1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = np.array(event.pos)
            for n in self.nodes:
                if is_inside_circle(pos, n.location, self.node_radius):
                    print(f"Clicked node {n.id} ({n.name})")
                    return n
        return None

    '''
    Read in nodes, edges, and groups from a file
    '''
    def parse(self, filename):
        filepath = Path(DATA_DIR) / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File {filename} not found in {DATA_DIR}")
        
        with open(filepath, 'r') as file:
            self.nodes = set()  # Ensure fresh
            self.edges = set()
            self.groups = []
            with open(filepath, "r") as file:
                counter = 0
                for line in file:
                    pass
                    line = line.strip()
                    if line[0] == '(':  # edge
                        names = line[1:-1].split(", ")
                        node1 = self.node_dict.get(names[0])
                        node2 = self.node_dict.get(names[1])
                        e = Edge(node1, node2)
                        self.edges.add(e)
                        node1.add_neighbor(node2.id)
                        node2.add_neighbor(node1.id)
                    elif line[0] == '[':  # group
                        names = line[1:-1].split(", ")
                        group = []
                        for name in names:
                            group.append(self.node_dict.get(name))
                        self.groups.append(group)
                    else:  # node
                        n = Node(counter, line)
                        counter += 1
                        self.nodes.add(n)
                        self.node_dict[line] = n  # append to node_dict for future lookup
