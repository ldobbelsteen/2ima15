from datastructures.DCEL import *
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
