from element import Graph, Node, Edge
from visualizer import GraphVisualizer

def create_3sat_sample_graph():
    g = Graph()

    # -------------------------------------------------
    # Clause 1: ( x1 OR ~x2 OR x3 )
    # -------------------------------------------------
    l1 = Node(node_id="x1_c1", name="x1")
    l2 = Node(node_id="~x2_c1", name="¬x2")
    l3 = Node(node_id="x3_c1", name="x3")

    # -------------------------------------------------
    # Clause 2: ( ~x1 OR x2 OR x3 )
    # -------------------------------------------------
    l4 = Node(node_id="~x1_c2", name="¬x1")
    l5 = Node(node_id="x2_c2", name="x2")
    l6 = Node(node_id="x3_c2", name="x3")

    # -------------------------------------------------
    # Clause 3: ( x1 OR ~x3 OR ~x2 )
    # -------------------------------------------------
    l7 = Node(node_id="x1_c3", name="x1")
    l8 = Node(node_id="~x3_c3", name="¬x3")
    l9 = Node(node_id="~x2_c3", name="¬x2")

    # Add them to graph
    for n in [l1, l2, l3, l4, l5, l6, l7, l8, l9]:
        g.add_node(n)

    # Create edges forming triangles for each clause
    # Clause 1 edges
    g.add_edge(Edge(l1, l2))
    g.add_edge(Edge(l2, l3))
    g.add_edge(Edge(l3, l1))

    # Clause 2 edges
    g.add_edge(Edge(l4, l5))
    g.add_edge(Edge(l5, l6))
    g.add_edge(Edge(l6, l4))

    # Clause 3 edges
    g.add_edge(Edge(l7, l8))
    g.add_edge(Edge(l8, l9))
    g.add_edge(Edge(l9, l7))

    # (Optional) Add edges between contradictory literals 
    # e.g., x1 <-> ¬x1, x2 <-> ¬x2, x3 <-> ¬x3
    # These edges help visualize interactions between clauses
    g.add_edge(Edge(l1, l4))  # x1 vs ¬x1
    g.add_edge(Edge(l2, l5))  # ¬x2 vs x2
    g.add_edge(Edge(l3, l8))  # x3 vs ¬x3

    return g

if __name__ == "__main__":
    # Build the 3-SAT sample graph
    graph_3sat = create_3sat_sample_graph()

    # Visualize it
    visualizer = GraphVisualizer(graph_3sat, width=1000, height=700)
    visualizer.run()
