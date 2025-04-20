from npvis.element.color import LIGHTGREY
from npvis.element.subelement import SubElement


class Edge(SubElement):
    def __init__(self, node1, node2, selected="false", color=LIGHTGREY, id=0):
        super().__init__(id, node1.name + node2.name, color)
        self.node1 = node1
        self.node2 = node2
        self.selected = selected
        self.default_color = color
