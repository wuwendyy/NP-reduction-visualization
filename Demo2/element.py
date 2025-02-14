class Node:
    def __init__(self, node_id, name, selected=False, color="", location=None):
        """
        A simple data container for node information.
        """
        self.node_id = node_id
        self.name = name
        self.selected = selected  # boolean
        self.color = color
        self.location = location  # (x, y) tuple or None

    def change_color(self, new_color):
        self.color = new_color

class Edge:
    def __init__(self, node1, node2, selected=False):
        """
        A simple data container for edge information.
        node1, node2 can be either Node objects or node IDs (depending on your design).
        """
        self.node1 = node1
        self.node2 = node2
        self.selected = selected

class Graph:
    def __init__(self):
        """
        A container for nodes and edges.
        """
        self.nodes = {}  # dict[node_id] = Node
        self.edges = []  # list of Edge objects

    def add_node(self, node: Node):
        self.nodes[node.node_id] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def get_nodes(self):
        return self.nodes.values()

    def get_edges(self):
        return self.edges

    def get_node_by_id(self, node_id):
        return self.nodes.get(node_id, None)
