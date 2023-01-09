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


class DCEL:
    """
    An implementation of a doubly connected edge list
    """

    def __init__(self, outer_boundary, holes):
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

        