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

    def __init__(self, vertice_list, edge_list):
        """
        Creates DCEL from input list of vertices and list of edges
        
        vertice_list:
            List of vertices represented as pairs (x, y)
            where x and y are the coordinates of the vertex
        edge_list:
            List of edges represented as pairs (u, v)
            where u and v are indices for vertice_list
        """
        self.half_edges = []
        self.vertices = []
        self.faces = []

        # Add vertices to DCEL
        for v in vertice_list:
            self.vertices.append(Vertex(v[0], v[1]))
        
        # Add Edges to DCEL
        for e in edge_list:
            # Vertices incident to the edge:
            v1 = self.vertices[e[0]]
            v2 = self.vertices[e[1]]
            # Create two half-edges corresponding to the edge
            half_edge_1 = HalfEdge(v1)
            half_edge_2 = HalfEdge(v2)

            # During construction maintain the list of all outgoing half edges
            # After construction each of these lists will be replaced with a single half edge
            if v1.incident_half_edge == None:
                v1.incident_half_edge = [half_edge_1]
            else:
                v1.incident_half_edge.append(half_edge_1)
            if v2.incident_half_edge == None:
                v2.incident_half_edge = [half_edge_2]
            else:
                v2.incident_half_edge.append(half_edge_2)

            # The half-edges are each others twins
            half_edge_1.twin = half_edge_2
            half_edge_2.twin = half_edge_1

            self.half_edges.append(half_edge_1)
            self.half_edges.append(half_edge_2)

        # Add Faces to DCEL
        for v in self.vertices:
            # Sort the outgoing edges clockwise order
            # DEGENERATE CASE: if two outgoing edges are colinear and point in the same direction this order is not well defined
            # TODO: Assign prev and next of each half-edge
            # TODO: set incident half-edge to a single half-edge instead of list
            pass
        
        # TODO: Add faces
            

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