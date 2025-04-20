import numpy as np
from npvis.element.color import LIGHTBLUE, LIGHTPINK

class Node:
    neighbors = []  # store all neighbor node_id

    def __init__(self, node_id, name, selected="false", color=LIGHTBLUE, location=np.array([0, 0])):
        self.node_id = node_id  # unique id
        self.name = name
        self.selected = selected
        self.color = color
        self.location = location
        self.default_color = color

    def change_color(self, new_color):
        self.color = new_color
        
    def toggle_highlight(self, highlight_color=LIGHTPINK):
        if self.color == self.default_color:
            self.change_color(highlight_color)
        else:
            self.change_color(self.default_color)

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        
    # def __repr__(self):
    #     return f"Node(ID={self.node_id}, Name={self.name}, Location={self.location.tolist()}, Neighbors={self.neighbors})"
    def __repr__(self):
        return f"Node(ID={self.node_id})"
    
    def __lt__(self, other):
        # define "less than" based on node_id
        return self.node_id < other.node_id
