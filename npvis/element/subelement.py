# all subelements need a color, name, id\
from npvis.element.color import LIGHTBLUE

class SubElement:
    def __init__(self, id, name, color=LIGHTBLUE):
        self.id = id
        self.name = name
        self.color = color
