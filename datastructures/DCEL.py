from enum import Enum
from datastructures.Rationals import Rationals as rat

class FaceType(Enum):
    OUTER = 0
    INTERIOR = 1
    HOLE = 2

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
        # Used for computing faces after insertions
        self.marked = False
        # Required for algorithm
        self.helper = None


class Face:
    def __init__(self):
        self.outer_component = None
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
            hole_outer_face.type = FaceType.HOLE
            self.process_boundary(hole_boundary, interior_face, hole_outer_face)
            self.faces.append(hole_outer_face)
        
        self.faces.append(interior_face)
        self.faces.append(boundary_outer_face)
        self.compute_vertex_types()

    
    def in_between(self, v1, v2, v1_incident_edge):
        """
        Checks whether the edge (v1, v2) falls in between v1_incident_edge and its prev
        """
        if edge_angle(v1, v1_incident_edge.twin.origin) > edge_angle(v1, v1_incident_edge.prev.origin):
            if (edge_angle(v1, v1_incident_edge.twin.origin) > edge_angle(v1, v2) and
                edge_angle(v1, v1_incident_edge.prev.origin) < edge_angle(v1, v2)):
                return True
            else:
                return False
        # The direction vertically downwards is included in the interval between v1_incident_edge
        # and its prev
        else:
            if (edge_angle(v1, v1_incident_edge.twin.origin) > edge_angle(v1, v2) or
                edge_angle(v1, v1_incident_edge.prev.origin) < edge_angle(v1, v2)):
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
            if v1_edge_incident_to_f.twin.origin.x == v2.x and v1_edge_incident_to_f.twin.origin.y == v2.y: #TODO: THIS HAPPENS IN CASE WE'RE INSERTING A DUPE.
                print(f"Inserting Duplicate edge: (({v1.x}, {v1.y}), ({v2.x}, {v2.y}))")
                return
            v1_edge_incident_to_f = v1_edge_incident_to_f.twin.next

        f = v1_edge_incident_to_f.incident_face

        # Find the outgoing half edge of v2 that comes after the new edge in counter-clockwise order
        v2_edge_incident_to_f = v2.incident_half_edge
        while not self.in_between(v2, v1, v2_edge_incident_to_f):
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
    

    def recompute_faces(self):
        new_faces = []
        for e in self.half_edges:
            if not e.marked:
                f = Face()
                # Even though a face might be subdivided it does not change type
                f.type = e.incident_face.type
                f.outer_component = e
                new_faces.append(f)
                while not e.marked:
                    e.incident_face = f
                    e.marked = True
                    e = e.next
        # Undo the marking for later computations
        for e in self.half_edges:
            e.marked = False
        self.faces = new_faces

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
        if (v1_edge_incident_to_f.twin.incident_face.type == FaceType.HOLE):
            v1_edge_incident_to_f.twin.incident_face.type = FaceType.HOLE
        elif (v2_edge_incident_to_f.twin.incident_face.type == FaceType.HOLE):
            v2_edge_incident_to_f.twin.incident_face.type = FaceType.HOLE
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
        def compute_vertex_types_of_boundary(vertex: Vertex, hole):
            # Find the topmost leftmost vertex
            v_max = vertex
            v = vertex.incident_half_edge.twin.origin
            while v != vertex:
                if v_max.y <= v.y and (v_max.y != v.y or v_max.x > v.x):
                    v_max = v
                v = v.incident_half_edge.twin.origin
            # we start at the top of the outer boundary where the topmost vertex is always located
            # we will always move downwards to the left for the first edge
            if not hole:
                v_max.type = VertexType.START
            else:
                v_max.type = VertexType.SPLIT

            left_of_polygon = not hole
            up = False

            # cycle trough all the edges of the face and their respective origins
            current_edge = v_max.incident_half_edge.next
            current_vertex = current_edge.origin
            while current_vertex != v_max:
                next_edge = current_edge.next
                next_vertex = next_edge.origin

                # current_edge is going down
                if current_vertex.y > next_vertex.y or (current_vertex.y == next_vertex.y and next_vertex.x > current_vertex.x):
                    # previous edge was also going down, direction did not change
                    if not up:
                        if left_of_polygon:
                            if not hole:
                                current_vertex.type = VertexType.REGULAR_RIGHT
                            else: 
                                current_vertex.type = VertexType.REGULAR_LEFT
                        else:
                            if not hole:
                                current_vertex.type = VertexType.REGULAR_LEFT
                            else:
                                current_vertex.type = VertexType.REGULAR_RIGHT
                    # direction changed from up to down
                    else:
                        up = False
                        if left_of_polygon == (leftmost_edge(current_edge, current_edge.prev.twin, up) == current_edge):
                            if not hole:
                                current_vertex.type = VertexType.START
                            else:
                                current_vertex.type = VertexType.SPLIT
                        else:
                            if not hole:
                                current_vertex.type = VertexType.SPLIT
                            else:
                                current_vertex.type = VertexType.START
                        left_of_polygon = not left_of_polygon

                # current_edge is going up
                else:
                    # previous edge was also going up, direction did not change
                    if up:
                        if left_of_polygon:
                            if not hole:
                                current_vertex.type = VertexType.REGULAR_RIGHT
                            else: 
                                current_vertex.type = VertexType.REGULAR_LEFT
                        else:
                            if not hole:
                                current_vertex.type = VertexType.REGULAR_LEFT
                            else:
                                current_vertex.type = VertexType.REGULAR_RIGHT
                    # direction changed from down to up
                    else:
                        up = True
                        if left_of_polygon == (leftmost_edge(current_edge, current_edge.prev.twin, up) != current_edge):
                            if not hole:
                                current_vertex.type = VertexType.END
                            else:
                                current_vertex.type = VertexType.MERGE
                        else:
                            if not hole:
                                current_vertex.type = VertexType.MERGE
                            else:
                                current_vertex.type = VertexType.END
                        left_of_polygon = not left_of_polygon

                # Move on to the next vertex
                current_edge = next_edge
                current_vertex = next_vertex

        # Do the same for the holes
        for f in self.faces:
            if f.type == FaceType.INTERIOR:
                compute_vertex_types_of_boundary(f.outer_component.origin, hole=False)
            if f.type == FaceType.HOLE:
                compute_vertex_types_of_boundary(f.outer_component.origin, hole=True)


def edge_angle(v1: Vertex, v2: Vertex):
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


def leftmost_edge(e1, e2, up):
        """
        Returns the leftmost_edge given two adjacent edges that both point upwards or both point downwards.
        """
        angle_e1 = edge_angle(e1.origin, e1.twin.origin)
        angle_e2 = edge_angle(e2.origin, e2.twin.origin)
        if up:
            if angle_e1 > angle_e2:
                return e1
            else:
                return e2
        else:
            if angle_e1[0] == 0 and angle_e2[0] == 0 or angle_e1[0] >= 2 and angle_e2[0] >= 2:
                if angle_e1 > angle_e2:
                    return e2
                else:
                    return e1
            else:
                if angle_e1 > angle_e2:
                    return e1
                else:
                    return e2


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