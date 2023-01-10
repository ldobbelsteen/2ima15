from datastructures.DCEL import DCEL, Vertex

# Triangulate a y-monotone partitioned polygon. The polygon
# should be represented by a double-connected egde list.
def triangulate_monotone_polygon(dcel: DCEL):

    # Triangulate each y-monotone partition
    for face in dcel.interior_faces():
        
        # Get face's vertices and represent them by a tuple. The first value
        # is the vertex and the second value indicates whether they are on the
        # left boundary (false) or the right boundary (true). TODO: implement
        # NOTE: think about how we can efficiently extract vertices from a face?
        # NOTE: think about how we can efficiently determine which side it is on?
        vertices: list[tuple[Vertex, bool]]  = []
        n_vertices = len(vertices)

        # Sort the vertices by their y-coordinates.
        # NOTE: could this step somehow be avoided?
        vertices.sort(key=lambda x: x.y)

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
                while len(stack) > 0 and True: # TODO: vertex sees top of stack
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
