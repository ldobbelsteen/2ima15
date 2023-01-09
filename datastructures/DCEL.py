# every (half-)edge:
#   origin (vertex)    
#   twin (half-edge)   
#   incident_face (face)
#   next (half-edge in cycle of incident face)
#   prev (half-edge in cycle of incident face)

# every vertex:
#   incident_edge (some outgoing edge)

# every face:
#   outer_component (half-edge of outer cycle)
#   inner_components (list of half-edges for inner cycles bounding faces)

class HalfEdge:
    def __init__(self, origin):
        self.origin = origin
        self.twin = None
        self.incident_face = None
        self.next = None
        self.prev = None


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incident_half_edge = None


class Face:
    def __init__(self):
        self.outer_component = None
        self.inner_components = []
        self.is_inner_face = None


class DCEL:
    """
    An implementation of a doubly connected edge list

    Attributes:
        half_edges: list of HalfEdges
        vertices: list of Vertices
        faces: list of Faces
    """

    def __init__(self, outer_boundary, holes=[]):
        """
        Creates DCEL from input
        
        outer_boundary:
            List of vertices represented as pairs (x, y)
            where x and y are the coordinates of the vertex,
            between each pair of consecutive vertices (and the first and last vertices) an edge is present
        holes:
            A list of lists of vertices adhering to the same format as outer_boundary.
        """
        self.half_edges = []
        self.vertices = []
        self.faces = []

        # Outer face incident to outer boundary
        boundary_outer_face = Face()
        boundary_outer_face.is_inner_face = False
        # The face that is the interior of the polygon 
        # (our input format guarantees that at initalization there is at most 1 such face)
        interior_face = Face()
        interior_face.is_inner_face = True

        # Initialize vertices and edges on outer boundary:
        self.process_boundary(outer_boundary, interior_face, boundary_outer_face)

        # Initialize vertices and edge on hole boundaries:
        for hole_boundary in holes:
            hole_outer_face = Face()
            hole_outer_face.is_inner_face = False
            self.process_boundary(hole_boundary, hole_outer_face, interior_face)
            self.faces.append(hole_outer_face)
        
        self.faces.append(interior_face)
        self.faces.append(boundary_outer_face)


    def insert_edge(self, v1, v2):
        """
        Inserts an edge between v1 and v2, v1 and v2 should be vertices in self.vertices
        """
        # TODO: implement this
        pass

    def process_boundary(self, boundary, inner_face, outer_face):
        """
        Auxiliary function that creates vertices and half edges corresponding to input boundary
        """
        old_h1 = None
        old_h2 = None
        v1 = Vertex(boundary[0]["x"], boundary[0]["y"])
        for i in range(1, len(boundary)):
            v2 = Vertex(boundary[i]["x"], boundary[i]["y"])
            h1 = HalfEdge(v1)
            h2 = HalfEdge(v2)

            v1.incident_half_edge = h1

            h1.twin = h2
            h2.twin = h1

            h1.incident_face = outer_face
            h2.incident_face = inner_face

            if i == 1:
                first_vertex = v1
                first_h1 = h1
                first_h2 = h2
            else:
                old_h1.next = h1
                old_h2.prev = h2
                h1.prev = old_h1
                h2.next = old_h2

            self.vertices.append(v1)
            self.half_edges.append(h1)
            self.half_edges.append(h2)

            old_h1 = h1
            old_h2 = h2
            v1 = v2
        
        # Add edges between the last and the first vertex in the list
        h1 = HalfEdge(v1)
        h2 = HalfEdge(first_vertex)

        v1.incident_half_edge = h1

        h1.twin = h2
        h2.twin = h1

        h1.incident_face = outer_face
        h2.incident_face = inner_face

        old_h1.next = h1
        old_h2.prev = h2
        h1.prev = old_h1
        h2.next = old_h2
        h1.next = first_h1
        h2.prev = first_h2
        first_h1.prev = h1
        first_h2.next = h2

        self.vertices.append(v1)
        self.half_edges.append(h1)
        self.half_edges.append(h2)

        outer_face.inner_components.append(h1)
        inner_face.outer_component = h2


# For testing purposes:
if __name__ == "__main__":
    dcel = DCEL([{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 2}], [[{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 2}], [{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 2}]])

    for v in dcel.vertices:
        if v.x == None or v.y == None or v.incident_half_edge == None:
            raise Exception("Nonevalue for vertex attribute")
        
        if not v.incident_half_edge.twin.next.origin == v:
            raise Exception("Incorrect DCEL")

    for h in dcel.half_edges:
        if h.origin == None or h.twin == None or h.incident_face == None or h.next == None or h.prev == None:
            raise Exception("Nonevalue for half edge attribute")

        if not h.next.twin.prev.next.next.twin == h:
            raise Exception("Incorrect DCEL")