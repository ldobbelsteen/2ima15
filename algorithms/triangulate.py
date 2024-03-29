from datastructures.dcel import DCEL, Vertex, HalfEdge, Face
from enum import Enum


def triangulate_monotone(dcel: DCEL, verbose=False, triangulate_convex_faces=True):
    """
    Triangulate a y-monotone partitioned polygon.
    """

    if verbose:
        print("Triangulating y-monotone pieces...")

    # Triangulate each y-monotone partition
    for face in dcel.interior_faces():
        # If face is already convex we don't need to triangulate it
        if not triangulate_convex_faces and is_convex(face):
            continue

        # Extract the left and right boundaries
        start = highest_leftmost(face.outer_component)
        left_boundary, right_boundary = extract_boundaries(start)

        # Merge the boundaries
        vertices = merge_boundaries(left_boundary, right_boundary)
        n_vertices = len(vertices)

        # Initialize stack with first two points
        stack = []
        stack.append(vertices[0])
        stack.append(vertices[1])

        # Handle all vertices and connect when necessary
        for i in range(2, n_vertices - 1):
            # If the i-th vertex and the top of the stack are on different boundaries
            if vertices[i][1] != stack[-1][1]:
                while len(stack) > 0:
                    vertex = stack.pop()
                    if len(stack) > 0:
                        dcel.insert_edge(vertices[i][0], vertex[0])
                stack.append(vertices[i - 1])
                stack.append(vertices[i])
            else:
                is_left_side = vertices[i][1]
                vertex = stack.pop()
                while len(stack) > 0 and ((get_direction(vertices[i][0], vertex[0], stack[-1][0])) == Direction.RIGHT if is_left_side else get_direction(vertices[i][0], vertex[0], stack[-1][0]) == Direction.LEFT):
                    vertex = stack.pop()
                    dcel.insert_edge(vertices[i][0], vertex[0])
                stack.append(vertex)
                stack.append(vertices[i])

        # Connect the last vertex to all vertices on
        # the stack, except for the first and last.
        stack.pop()
        while len(stack) > 1:
            vertex = stack.pop()
            dcel.insert_edge(vertices[-1][0], vertex[0])

    dcel.recompute_faces()
    if verbose:
        print("Finished triangulating y-monotone pieces.")


def highest_leftmost(edge: HalfEdge) -> HalfEdge:
    """
    Locate the half edge with the highest and leftmost origin in a half cycle.
    """

    best = edge
    current = edge.next
    while current != edge:
        if current.origin.y >= best.origin.y:
            if current.origin.y > best.origin.y:
                best = current
            elif current.origin.x < best.origin.x:
                best = current
        current = current.next
    return best


def extract_boundaries(highest_leftmost: HalfEdge) -> tuple[list[Vertex], list[Vertex]]:
    """
    Extract the left and right boundaries of a y-monotone polygon using its
    highest and leftmost vertex.
    """

    left_boundary: list[Vertex] = [highest_leftmost.origin]
    right_boundary: list[Vertex] = []

    switched_direction = False
    current = highest_leftmost.prev

    while current != highest_leftmost:
        if current.prev.origin.y > current.origin.y:
            switched_direction = True
        if not switched_direction:
            left_boundary.append(current.origin)
        else:
            right_boundary.append(current.origin)
        current = current.prev

    right_boundary.reverse()

    return (left_boundary, right_boundary)


def merge_boundaries(left_boundary: list[Vertex], right_boundary: list[Vertex]) -> list[tuple[Vertex, bool]]:
    """
    Merge boundaries into a list of vertices sorted decreasingly by their
    y-coordinates. Vertices are accompanied by a boolean indicating whether
    they are on the left or right boundary (true = left, false = right).
    """

    result: list[tuple[Vertex, bool]] = []

    left_index = 0
    right_index = 0
    for _ in range(len(left_boundary) + len(right_boundary)):
        left_finished = left_index == len(left_boundary)
        right_finished = right_index == len(right_boundary)
        if left_finished and not right_finished:
            result.append((right_boundary[right_index], False))
            right_index += 1
        elif right_finished and not left_finished:
            result.append((left_boundary[left_index], True))
            left_index += 1
        else:
            if left_boundary[left_index].y >= right_boundary[right_index].y:
                result.append((left_boundary[left_index], True))
                left_index += 1
            else:
                result.append((right_boundary[right_index], False))
                right_index += 1

    return result


class Direction(Enum):
    LEFT = 1
    COLINEAR = 2
    RIGHT = 3


def get_direction(first: Vertex, middle: Vertex, end: Vertex) -> Direction:
    """
    Return whether three vertices form a left turn or a right turn. True
    is returned when they form a left turn and false when they form a right
    turn.

    Based on https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
    """

    first_end = (end.x - first.x, end.y - first.y)
    first_middle = (middle.x - first.x, middle.y - first.y)
    direction = first_end[0] * \
        first_middle[1] - first_middle[0] * first_end[1]

    if direction < 0:
        return Direction.LEFT
    elif direction > 0:
        return Direction.RIGHT
    else:
        return Direction.COLINEAR


def is_convex(face: Face):
    """
    Returns whether a face is convex by walking around its boundary and seeing if all angles make a right turn
    """
    edge = face.outer_component
    if get_direction(edge.origin, edge.next.origin, edge.next.next.origin) == Direction.LEFT:
        return False
    edge = edge.next
    while edge != face.outer_component:
        if get_direction(edge.origin, edge.next.origin, edge.next.next.origin) == Direction.LEFT:
            return False
        edge = edge.next
    return True
