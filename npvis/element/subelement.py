# all subelements need a color, name, id\
from npvis.element.color import LIGHTBLUE, LIGHTPINK

class SubElement:
    def __init__(self, id, name, default_color=LIGHTBLUE, highlight_color=LIGHTPINK, selected=False):
        self.id = id
        self.name = name
        self.color = default_color
        self.default_color = default_color
        self.highlight_color = highlight_color
        self.selected = selected

    def toggle_highlight(self):
        if self.color == self.default_color:
            self.color = self.highlight_color
        else:
            self.color = self.default_color
