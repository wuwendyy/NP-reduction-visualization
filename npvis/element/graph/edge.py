from npvis.element.color import LIGHTGREY

class Edge:
    def __init__(self, node1, node2, selected="false", color=LIGHTGREY):
        self.node1 = node1
        self.node2 = node2
        self.selected = selected
        self.color = color
        self.default_color = color
