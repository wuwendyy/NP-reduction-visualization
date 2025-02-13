class Node:
    def __init__(self, node_id, name, selected="false", color="", location=""):
        self.node_id = node_id
        self.name = name
        self.selected = selected
        self.color = color
        self.location = location

    def change_color(self, new_color):
        self.color = new_color


class Edge:
    def __init__(self, node1, node2, selected="false"):
        self.node1 = node1
        self.node2 = node2
        self.selected = selected
