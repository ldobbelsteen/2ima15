from datastructures.DCEL import DCEL, Vertex, Face, HalfEdge


def triangulate_monotone_polygon(dcel: DCEL):
    """
    Triangulate a y-monotone partitioned polygon.
    """

    # Triangulate each y-monotone partition
    for face in dcel.interior_faces():

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
                        dcel.insert_edge(vertices[i], vertex, face)
                stack.append(vertices[i - 1])
                stack.append(vertices[i])
            else:
                vertex = stack.pop()
                while len(stack) > 0 and True:  # TODO: vertex sees top of stack condition
                    vertex = stack.pop()
                    dcel.insert_edge(vertices[i], vertex, face)
                stack.append(vertex)
                stack.append(vertices[i])

        # Connect the last vertex to all vertices on
        # the stack, except for the first and last.
        stack.pop()
        while len(stack) > 1:
            vertex = stack.pop()
            dcel.insert_edge(vertices[-1], vertex, face)


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

    # TODO: implement
    return ([], [])


def merge_boundaries(left_boundary: list[Vertex], right_boundary: list[Vertex]) -> list[tuple[Vertex, bool]]:
    """
    Merge boundaries into a list of vertices sorted decreasingly by their
    y-coordinates. Vertices are accompanied by a boolean indicating whether
    they are on the left or right boundary (true = left, false = right).
    """

    # TODO: implement
    return []
