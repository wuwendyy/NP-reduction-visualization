import pygame
import numpy as np

def draw_thick_bezier_curve(screen, start, control, end, color, width=3):
    """
    Draws a thick quadratic Bézier curve from start → control → end.

    Args:
        screen: Pygame surface.
        start: Start position (numpy array).
        control: Control point for the Bézier curve.
        end: End position.
        color: RGB color tuple.
        width: Line thickness.
    """
    num_segments = 30  # Controls smoothness of the curve
    points = []

    for t in np.linspace(0, 1, num_segments):
        # Quadratic Bézier interpolation
        point = (1 - t) ** 2 * start + 2 * (1 - t) * t * control + t ** 2 * end
        points.append(point.astype(int))

    # Draw curve using multiple slightly offset lines to simulate thickness
    for i in range(-width // 2, width // 2 + 1):
        offset_points = [(p[0] + i, p[1] + i) for p in points]
        pygame.draw.lines(screen, color, False, offset_points, 2)

def find_best_control_point(start_pos, end_pos, nodes, node_radius):
    """
    Dynamically finds the best control point for a Bézier curve to avoid overlapping nodes.

    Args:
        start_pos: Start position of the edge.
        end_pos: End position of the edge.
        nodes: List of nodes to check against.
        node_radius: Radius of nodes.

    Returns:
        control_point: Adjusted control point for a smooth Bézier curve.
    """
    mid_point = (start_pos + end_pos) / 2
    displacement = np.array([-(end_pos[1] - start_pos[1]), end_pos[0] - start_pos[0]])
    displacement = displacement / np.linalg.norm(displacement) * node_radius * 2.5  # Slightly larger curve

    control_point = mid_point + displacement
    iterations = 0
    max_iterations = 5

    # Ensure control point does not collide and maintains a safe distance
    while any(is_point_too_close(control_point, node.location, node_radius * 1.8) for node in nodes):
        displacement *= 1.3  # Increase the curvature step-by-step
        control_point = mid_point + displacement
        iterations += 1
        if iterations >= max_iterations:
            break  # Prevent infinite loops

    return control_point

def is_point_too_close(point, node_location, min_distance):
    """
    Checks if a given point is too close to a node, ensuring a buffer zone.

    Args:
        point: The point to check.
        node_location: The location of the node.
        min_distance: The minimum distance required.

    Returns:
        bool: True if the point is too close, False otherwise.
    """
    return np.linalg.norm(point - node_location) < min_distance

def has_overlapping_edge(edge, nodes, node_radius):
    """
    Check if an edge between two nodes intersects with any other node along its path.

    Args:
        edge: The edge being checked.
        nodes: List of all nodes in the graph.
        node_radius: The radius of a node.

    Returns:
        bool: True if the edge overlaps with any node (other than its endpoints), False otherwise.
    """
    start_pos = edge.node1.location
    end_pos = edge.node2.location

    for node in nodes:
        if node == edge.node1 or node == edge.node2:
            continue  # Skip endpoints

        if is_point_near_line(node.location, start_pos, end_pos, threshold=node_radius * 1.5):
            return True  # The edge passes too close to another node

    return False

def is_point_near_line(point, line_start, line_end, threshold):
    """
    Determines if a point (node) is near the line segment between two other points.

    Args:
        point: The location of the node to check.
        line_start: The start position of the edge.
        line_end: The end position of the edge.
        threshold: Distance threshold to determine "near" proximity.

    Returns:
        bool: True if the point is near the line segment, False otherwise.
    """
    line_vector = line_end - line_start
    point_vector = point - line_start
    line_length = np.linalg.norm(line_vector)

    if line_length == 0:
        return False  # Avoid division by zero (edge is a point)

    # Project the point onto the line using dot product
    projection = np.dot(point_vector, line_vector) / line_length
    projected_point = line_start + (projection / line_length) * line_vector

    # Check if projection is within the segment bounds
    if np.dot(projected_point - line_start, projected_point - line_end) > 0:
        return False  # The projected point is outside the segment

    # Calculate distance from node to the closest point on the edge
    distance = np.linalg.norm(point - projected_point)
    return distance < threshold
