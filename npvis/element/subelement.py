from abc import abstractmethod

# all subelements need a color, name, id
class SubElement:
    def __init__(self, id, name, color):
        self.id = id
        self.name = name
        self.color = color
