from enum import Enum
from datastructures.Rationals import Rationals as rat

class FaceType(Enum):
    OUTER = 0
    INTERIOR = 1
    CONNECTED_HOLE = 2
    DISCONNECTED_HOLE = 3

class VertexType(Enum):
    START = 0
    END = 1
    MERGE = 2
    SPLIT = 3
    REGULAR_RIGHT = 4
    REGULAR_LEFT = 5

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
#   inner_components (list of half-edges for inner cycles bounding faces) REDUNDANT?

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incident_half_edge = None
        # Required for algorithm
        self.type = None # TODO: compute this in DCEL constructor


class HalfEdge:
    def __init__(self, origin: Vertex):
        self.origin = origin
        self.twin = None
        self.incident_face = None
        self.next = None
        self.prev = None
        # Required for algorithm
        self.helper = None


class Face:
    def __init__(self):
        self.outer_component = None
        #self.inner_components = []
        self.type = None


class DCEL:
    """
    An implementation of a doubly connected edge list

    Attributes:
        half_edges: list of HalfEdges
        vertices: list of Vertices
        faces: list of Faces
    """

    def __init__(self, outer_boundary: list[dict], holes: list[dict]):
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
        boundary_outer_face.type = FaceType.OUTER
        # The face that is the interior of the polygon 
        # (our input format guarantees that at initalization there is at most 1 such face)
        interior_face = Face()
        interior_face.type = FaceType.INTERIOR

        # Initialize vertices and edges on outer boundary:
        self.process_boundary(outer_boundary, interior_face, boundary_outer_face)

        # Initialize vertices and edge on hole boundaries:
        for hole_boundary in holes:
            hole_outer_face = Face()
            hole_outer_face.type = FaceType.DISCONNECTED_HOLE
            self.process_boundary(hole_boundary, interior_face, hole_outer_face)
            self.faces.append(hole_outer_face)
        
        self.faces.append(interior_face)
        self.faces.append(boundary_outer_face)


    def edge_angle(self, v1: Vertex, v2: Vertex):
            """
            Returns a pair (a, b), where a is either 0, 1, 2, or 3, and b is the slope of the edge (v1, v2) (or None if the slope is (-)infinity).
            a = 0 implies that (v1, v2) points to the right
            a = 1 implies that (v1, v2) points upwards
            a = 2 implies that (v1, v2) points to the left
            a = 3 implies that (v1, v2) points downwards
            """
            # Edge points to the right
            if v2.x-v1.x > 0:
                return (0, rat(v2.y - v1.y, v2.x - v1.x))
            # Edge points to the left
            elif v2.x-v1.x < 0:
                return (2, rat(v2.y - v1.y, v2.x - v1.x))
            # Edge points vertically upwards
            elif v2.y > v1.y:
                return (1, None)
            # Edge points vertically downwards
            else:
                return (3, None)
    
    def in_between(self, v1, v2, v1_incident_edge):
        """
        Checks whether the edge (v1, v2) falls in between v1_incident_edge and its prev
        """
        if self.edge_angle(v1, v1_incident_edge.twin.origin) > self.edge_angle(v1, v1_incident_edge.prev.origin):
            if (self.edge_angle(v1, v1_incident_edge.twin.origin) > self.edge_angle(v1, v2) and
                self.edge_angle(v1, v1_incident_edge.prev.origin) < self.edge_angle(v1, v2)):
                return True
            else:
                return False
        # The direction vertically downwards is included in the interval between v1_incident_edge
        # and its prev
        else:
            if (self.edge_angle(v1, v1_incident_edge.twin.origin) > self.edge_angle(v1, v2) or
                self.edge_angle(v1, v1_incident_edge.prev.origin) < self.edge_angle(v1, v2)):
                return True
            else:
                return False


    def insert_edge(self, v1: Vertex, v2: Vertex):
        """
        Inserts an edge between v1 and v2, v1 and v2 should be vertices in self.vertices.
        """

        # Find the outgoing half edge of v1 that comes after the new edge in counter-clockwise order
        v1_edge_incident_to_f = v1.incident_half_edge
        while not self.in_between(v1, v2, v1_edge_incident_to_f):
            v1_edge_incident_to_f = v1_edge_incident_to_f.twin.next

        f = v1_edge_incident_to_f.incident_face

        # Find the outgoing half edge of v2 that comes after the new edge in counter-clockwise order
        v2_edge_incident_to_f = v2.incident_half_edge
        while v2_edge_incident_to_f.incident_face != f:
            v2_edge_incident_to_f = v2_edge_incident_to_f.twin.next

        h1 = HalfEdge(v1)
        h2 = HalfEdge(v2)

        h1.twin = h2
        h2.twin = h1

        h1.next = v2_edge_incident_to_f
        h1.prev = v1_edge_incident_to_f.prev
        h2.next = v1_edge_incident_to_f
        h2.prev = v2_edge_incident_to_f.prev

        v1_edge_incident_to_f.prev.next = h1
        v2_edge_incident_to_f.prev.next = h2
        v1_edge_incident_to_f.prev = h2
        v2_edge_incident_to_f.prev = h1

        # In the case where the inserted edge connects a not yet connected hole boundary to 
        # the graph connected to the outer boundary we do not need to alter any faces
        if (v1_edge_incident_to_f.twin.incident_face.type == FaceType.DISCONNECTED_HOLE):
            v1_edge_incident_to_f.twin.incident_face.type = FaceType.CONNECTED_HOLE
        elif (v2_edge_incident_to_f.twin.incident_face.type == FaceType.DISCONNECTED_HOLE):
            v2_edge_incident_to_f.twin.incident_face.type = FaceType.CONNECTED_HOLE
        else:
            # Split the intersected face into two new faces
            f1 = Face()
            f1.type = FaceType.INTERIOR
            f1.outer_component = h1
            edge = h1
            h1.incident_face = f1
            edge = edge.next
            while edge != h1:
                edge.incident_face = f1
                edge = edge.next
            f2 = Face()
            f2.type = FaceType.INTERIOR
            f2.outer_component = h2
            edge = h2
            h2.incident_face = f2
            edge = edge.next
            while edge != h2:
                edge.incident_face = f2
                edge = edge.next
            self.faces.remove(f)
            self.faces.append(f1)
            self.faces.append(f2)
    

    def insert_edge_with_face(self, v1: Vertex, v2: Vertex, f: Face):
        """
        [DEPRECATED]
        Inserts an edge between v1 and v2 through face f, 
        v1 and v2 should be vertices in self.vertices and f should be a face in self.faces.
        """

        v1_edge_incident_to_f = v1.incident_half_edge
        while v1_edge_incident_to_f.incident_face != f:
            v1_edge_incident_to_f = v1_edge_incident_to_f.twin.next

        v2_edge_incident_to_f = v2.incident_half_edge
        while v2_edge_incident_to_f.incident_face != f:
            v2_edge_incident_to_f = v2_edge_incident_to_f.twin.next

        h1 = HalfEdge(v1)
        h2 = HalfEdge(v2)

        h1.twin = h2
        h2.twin = h1

        h1.next = v2_edge_incident_to_f
        h1.prev = v1_edge_incident_to_f.prev
        h2.next = v1_edge_incident_to_f
        h2.prev = v2_edge_incident_to_f.prev

        v1_edge_incident_to_f.prev.next = h1
        v2_edge_incident_to_f.prev.next = h2
        v1_edge_incident_to_f.prev = h2
        v2_edge_incident_to_f.prev = h1

        # In the case where the inserted edge connects a not yet connected hole boundary to 
        # the graph connected to the outer boundary we do not need to alter any faces
        if (v1_edge_incident_to_f.twin.incident_face.type == FaceType.DISCONNECTED_HOLE):
            v1_edge_incident_to_f.twin.incident_face.type = FaceType.CONNECTED_HOLE
        elif (v2_edge_incident_to_f.twin.incident_face.type == FaceType.DISCONNECTED_HOLE):
            v2_edge_incident_to_f.twin.incident_face.type = FaceType.CONNECTED_HOLE
        else:
            # Split the intersected face into two new faces
            f1 = Face()
            f1.type = FaceType.INTERIOR
            f1.outer_component = h1
            edge = h1
            h1.incident_face = f1
            edge = edge.next
            while edge != h1:
                edge.incident_face = f1
                edge = edge.next
            f2 = Face()
            f2.type = FaceType.INTERIOR
            f2.outer_component = h2
            edge = h2
            h2.incident_face = f2
            edge = edge.next
            while edge != h2:
                edge.incident_face = f2
                edge = edge.next
            self.faces.remove(f)
            self.faces.append(f1)
            self.faces.append(f2)


    def delete_edge(self, e: HalfEdge):
        """
        Deletes the edge e, e should be a vertex in self.vertices
        """
        # TODO: implement this
        pass


    def interior_faces(self):
        """
        Returns the faces that are contained in the polygon.
        """
        return [f for f in self.faces if f.type == FaceType.INTERIOR]


    def format_solution(self):
        """
        Converts the DCEL to the output format:
        https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2023/#instance-format
        """
        polygons = list()

        # Each interior face corresponds to a polygon:
        for f in self.interior_faces():
            polygon = list()
            e = f.outer_component
            polygon.append({"x": e.origin.x, "y": e.origin.y})
            e = e.next
            while e != f.outer_component:
                polygon.append({"x": e.origin.x, "y": e.origin.y})
                e = e.next
            polygons.append(polygon)
        
        return {"polygons": polygons}
    

    def process_boundary(self, boundary: list[dict], inner_face: Face, outer_face: Face):
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

            # h1 goes counter-clockwise along the outer face
            # h2 goes clock-wise along the inner face
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

        #outer_face.inner_components.append(h1)
        if outer_face.type == FaceType.OUTER:
            inner_face.outer_component = h2
        else:
            outer_face.outer_component = h1

    
    def compute_vertex_types(self):
        # Find the topmost vertex (if there are multiple such vertices we take the first)
        v_max = self.vertices[0]
        for v in self.vertices:
            if v_max.y > v.y:
                v_max = v
        # we start at the top of the outer boundery where the topmost vertex is always located
        # we will always move downwards for the first edge 
        v_max.type = VertexType.START
        up = False
        # cycle trough all the edges of the face and their respective origins 
        current_edge = v_max.incident_half_edge.next
        current_vertex = current_edge.origin
        if v_max.x < current_vertex.x:
            right = True
        else:
            right = False
        while current_vertex != v_max:
            next_edge = current_edge.next
            next_vertex = next_edge.origin
            if current_vertex.y >= next_vertex.y:
                next_up = False
                if not up:
                    #if we go clockwise going down means P is to our left 
                    if right:
                        current_vertex.type = VertexType.REGULAR_LEFT
                    else: 
                        current_vertex.type = VertexType.REGULAR_RIGHT
                else:   
                    print("hier moet ik nog tussen start  en split checken ")
            else:
                next_up = True
                if up:
                    if right:
                        current_vertex.type = VertexType.REGULAR_RIGHT
                    else: 
                        current_vertex.type = VertexType.REGULAR_LEFT
                else:
                    print("hier moet ik nog tussen end  en merge checken ")
            current_edge = next_edge
            current_vertex = next_vertex
            up = next_up
            

                



        



            



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