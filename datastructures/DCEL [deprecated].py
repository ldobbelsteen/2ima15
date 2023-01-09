import math

# This file is deprecated as the way I implemented the DCEL here does not easily work for polygons with holes.

class HalfEdge:
    def __init__(self, origin):
        self.origin = origin
        self.twin = None
        self.incident_face = None
        self.next = None
        self.prev = None
        # Angle with respect to x-axis
        self.angle = None
    
    def compute_angle(self):
        # THIS FUNCTION EXPLICITLY COMPUTES ANGLES, WHICH MIGHT LEAD TO ROUNDING ERRORS
        if self.twin == None:
            raise Exception("Can not compute angle: twin undefined.")
        dx = self.twin.origin.x - self.origin.x
        dy = self.twin.origin.y - self.origin.y
        length = math.sqrt(dx*dx + dy*dy)
        if dy > 0:
            self.angle = math.acos(dx/length)
        else:
            self.angle = 2*math.pi - math.acos(dx/length)

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

            # Now that the twins have been assigned the angles can be computed
            half_edge_1.compute_angle()
            half_edge_2.compute_angle()

            self.half_edges.append(half_edge_1)
            self.half_edges.append(half_edge_2)

        # Assign prev and next of each half-edge
        for v in self.vertices:
            # Sort the outgoing edges in counter-clockwise order
            v.incident_half_edge.sort(key=lambda half_edge: half_edge.angle)
            # Assign prev and next of each half-edge
            nr_of_outgoing_edges = len(v.incident_half_edge)
            for i in range(nr_of_outgoing_edges):
                v.incident_half_edge[i].prev = v.incident_half_edge[(i+1) % nr_of_outgoing_edges].twin
                v.incident_half_edge[i].next = v.incident_half_edge[i].twin.prev # TODO: I suspect this doesnt work, can be fixed by assigning next after all the prevs have been assigned
            # TODO: set incident half-edge to a single half-edge instead of list
        
        # TODO: Add faces
        # Since we have holes it is possible for two half-edges to be incident to the same face
        # while not being part of the same chain of half-edges.
        # I do not know how to identify this case with the current implementation.
            

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