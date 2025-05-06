import numpy as np
from npvis.element.color import LIGHTBLUE, LIGHTPINK
from npvis.element.subelement import SubElement


class Node(SubElement):
    neighbors = []  # store all neighbor node_id

    def __init__(self, id, name, color=LIGHTBLUE, location=np.array([0, 0])):
        super().__init__(id, name, color, LIGHTPINK)
        self.location = location

    def change_color(self, new_color):
        self.color = new_color

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        
    # def __repr__(self):
    #     return f"Node(ID={self.id}, Name={self.name}, Location={self.location.tolist()}, Neighbors={self.neighbors})"
    def __repr__(self):
        return f"Node(ID={self.id})"
    
    def __lt__(self, other):
        # define "less than" based on node_id
        return self.id < other.id
