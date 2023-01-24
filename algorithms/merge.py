from datastructures.dcel import *
from algorithms.triangulate import get_direction, Direction


def bruteforce_merge_adjacent_faces(dcel: DCEL):
    """
    Merges faces by repeatedly picking an arbitrary face and attempting to merge it with an arbitrary neighbour.
    It keeps doing this until this is no longer possible.
    """

    def merge_face(face: Face):
        edge = face.outer_component
        if convex_after_deleting(edge):
            dcel.delete_edge(edge)
            return True
        edge = edge.next
        while edge != face.outer_component:
            if convex_after_deleting(edge):
                dcel.delete_edge(edge)
                return True
            edge = edge.next
        return False

    def convex_after_deleting(edge: HalfEdge):
        """
        Returns whether the face resulting from the deletion of edge will be convex.
        """
        # We can't merge with an exterior face
        if edge.twin.incident_face.type != FaceType.INTERIOR:
            return False

        # If the faces share multiple edges we can't delete only one of them.
        # The current implementation of the DCEL does not allow for the deletion of multiple edges at once
        # Note that since we don't introduce steiner points two different convex faces can in fact never share more than one edge.
        if edge.twin.incident_face == edge.next.twin.incident_face:
            return False

        # If neither of the two new corners in the polygon are concave, we can merge
        if (get_direction(edge.twin.prev.origin, edge.next.origin, edge.next.next.origin) != Direction.LEFT and
                get_direction(edge.prev.origin, edge.origin, edge.twin.next.next.origin) != Direction.LEFT):
            return True
        else:
            return False

    did_merge = True
    while did_merge:
        did_merge = False
        for face in dcel.interior_faces():
            did_merge = merge_face(face)
            if did_merge:
                break


def bruteforce_merge_indirect_neighbours(dcel: DCEL):
    """
    Merges (non-adjacent) faces by repeatedly picking an arbitrary face and attempting to merge its neightbours with each other.
    """

    # This face will be set as the incident face of the twins of any new edges we will be adding.
    dummy_face = Face()
    dummy_face.type = FaceType.OUTER

    def merge_neighbouring_faces(face):
        edge1 = face.outer_component
        edge2 = edge1.next
        while edge2 != face.outer_component:
            if can_merge(edge1, edge2):
                merge(edge1, edge2)
                return True
            edge2 = edge2.next
        edge1 = edge1.next

        while edge1 != face.outer_component:
            edge2 = edge1.next
            while edge2 != face.outer_component:
                if can_merge(edge1, edge2):
                    merge(edge1, edge2)
                    return True
                edge2 = edge2.next
            edge1 = edge1.next
        
        return False
    
    def can_merge(edge1, edge2):
        """
        Returns whether edge1.twin.incident_face and edge2.twin.incident face can be merged into a convex face
        """

        # We can't merge exterior faces
        if edge1.twin.incident_face.type != FaceType.INTERIOR or edge2.twin.incident_face.type != FaceType.INTERIOR:
            return False

        # If neither of the four new corners in the polygon are concave, we can merge
        edge1_twin_prev = edge1.twin.prev
        while edge1_twin_prev.origin == edge1.twin.origin:
            edge1_twin_prev = edge1_twin_prev.prev
        edge2_twin_next = edge2.twin.next
        while edge2_twin_next.twin.origin == edge2.origin:
            edge2_twin_next = edge2_twin_next.next

        edge2_twin_prev = edge2.twin.prev
        while edge2_twin_prev.origin == edge2.twin.origin:
            edge2_twin_prev = edge2_twin_prev.prev
        edge1_twin_next = edge1.twin.next
        while edge1_twin_next.twin.origin == edge1.origin:
            edge1_twin_next = edge1_twin_next.next
        
        if ((edge1.twin.origin != edge2.origin and
            get_direction(edge1_twin_prev.origin, edge1.twin.origin, edge2.origin) != Direction.LEFT and
            get_direction(edge1.twin.origin, edge2.origin, edge2_twin_next.twin.origin) != Direction.LEFT or
            edge1.twin.origin == edge2.origin and
            get_direction(edge1_twin_prev.origin, edge2.origin, edge2_twin_next.twin.origin) != Direction.LEFT
            ) and
            (edge2.twin.origin != edge1.origin and
            get_direction(edge2_twin_prev.origin, edge2.twin.origin, edge1.origin) != Direction.LEFT and
            get_direction(edge2.twin.origin, edge1.origin, edge1_twin_next.twin.origin) != Direction.LEFT or
            edge2.twin.origin == edge1.origin and
            get_direction(edge2_twin_prev.origin, edge1.origin, edge1_twin_next.twin.origin) != Direction.LEFT
            )):
            return True
        else:
            return False

    def merge(edge1, edge2):
        h1 = HalfEdge(edge1.twin.origin)
        h2 = HalfEdge(edge2.origin)
        h1.twin = h2
        h2.twin = h1

        h1.prev = edge1.twin.prev
        edge1.twin.prev.next = h1
        h1.next = edge2.twin.next
        edge2.twin.next.prev = h1
        h2.incident_face = dummy_face

        h3 = HalfEdge(edge2.twin.origin)
        h4 = HalfEdge(edge1.origin)
        h3.twin = h4
        h4.twin = h3

        h3.prev = edge2.twin.prev
        edge2.twin.prev.next = h3
        h3.next = edge1.twin.next
        edge1.twin.next.prev = h3
        h4.incident_face = dummy_face

        edge = h1
        while edge.incident_face != edge1.twin.incident_face:
            edge.incident_face = edge1.twin.incident_face
            edge = edge.next
        edge.incident_face.outer_component = edge
        dcel.faces.remove(edge2.twin.incident_face)

        edge1.twin.incident_face = dummy_face
        edge2.twin.incident_face = dummy_face


    did_merge = True
    while did_merge:
        did_merge = False
        for face in dcel.interior_faces():
            did_merge = merge_neighbouring_faces(face)
            if did_merge:
                break



