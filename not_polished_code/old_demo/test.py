import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Sample 3-SAT formula: (¬x1 ∨ x2 ∨ x3) ∧ (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ x4)
cnf_formula = [["¬x1", "x2", "x3"], ["x1", "¬x2", "x3"], ["¬x1", "x2", "x4"]]

# Build the graph representation
G = nx.Graph()

# Add literal nodes
for clause in cnf_formula:
    for literal in clause:
        if not G.has_node(literal):
            G.add_node(literal)

# Ensure all 9 literals are included
all_literals = {"¬x1", "x1", "x2", "¬x2", "x3", "x4"}
for lit in all_literals:
    G.add_node(lit)

# Add edges for literals in the same clause (clause constraints)
for clause in cnf_formula:
    G.add_edges_from([(clause[0], clause[1]), (clause[1], clause[2]), (clause[2], clause[0])])

# Add edges for complementary literals (~x <-> x constraints)
literals = set(node for clause in cnf_formula for node in clause)
for literal in literals:
    neg_literal = "¬" + literal if "¬" not in literal else literal[1:]
    if neg_literal in all_literals and literal != neg_literal:
        G.add_edge(literal, neg_literal)

# Visualization function
def draw_graph(highlight_nodes=None, error_edges=None, title="SAT to Independent Set Conversion"):
    plt.clf()
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))
    pos = nx.spring_layout(G)
    
    # Upper half - formula visualization
    axs[0].text(0.5, 0.5, "ϕ = (¬x1 ∨ x2 ∨ x3) ∧ (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ x4)", 
                fontsize=12, ha='center', va='center', fontweight='bold')
    axs[0].axis("off")
    
    # Lower half - graph visualization
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', ax=axs[1])
    
    if highlight_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=highlight_nodes, node_color='green', ax=axs[1])
    
    if error_edges:
        nx.draw_networkx_edges(G, pos, edgelist=error_edges, edge_color='red', width=2, ax=axs[1])
    
    axs[1].set_title(title)
    plt.show()

# Callback function for problem setup correspondence
def check_problem_setup(event):
    error_edges = []  # Example placeholder
    draw_graph(error_edges=error_edges, title="Checking Problem Setup Correspondence")

# Callback function for solution conversion
def show_solution(event):
    highlight_nodes = ["x2", "x3", "x4"]  # Example selection
    draw_graph(highlight_nodes=highlight_nodes, title="Solution Conversion Visualization")

# Create UI buttons
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
ax_problem = plt.axes([0.1, 0.05, 0.3, 0.075])
ax_solution = plt.axes([0.5, 0.05, 0.3, 0.075])
btn_problem = Button(ax_problem, "Check Setup")
btn_solution = Button(ax_solution, "Show Solution")
btn_problem.on_clicked(check_problem_setup)
btn_solution.on_clicked(show_solution)

# Initial drawing
draw_graph()
plt.show()
