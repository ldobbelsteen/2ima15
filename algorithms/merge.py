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

    did_merge = True
    while did_merge:
        did_merge = False
        for face in dcel.interior_faces():
            did_merge = merge_face(face)
            if did_merge:
                break


def hertel_mehlhorn(dcel: DCEL, permutation=None):
    diagonals = [h for h in dcel.half_edges if h.incident_face.type == FaceType.INTERIOR and h.twin.incident_face.type == FaceType.INTERIOR]
    # Permute the diagonals according to input function if it was given
    if permutation:
        permutation(diagonals=diagonals)

    # For each diagonal, remove it if the resulting face is convex
    for i in range(len(diagonals)):
        diagonals[i].twin.marked = True
        if not diagonals[i].marked and convex_after_deleting(diagonals[i]):
            dcel.delete_edge(diagonals[i])

    # Unmark all edges for later computations:
    for h in dcel.half_edges:
        h.marked = False
            

def bruteforce_merge_indirect_neighbours(dcel: DCEL):
    """
    Merges (non-adjacent) faces by repeatedly picking an arbitrary face and attempting to merge its neightbours with each other.
    """

    # This face will be set as the incident face of the twins of any new edges we will be adding.
    dummy_face = Face()
    dummy_face.type = FaceType.OUTER

    def merge_neighbouring_faces(face):
        """
        Iterates over all pairs of edges of face, attempting to merge their incident polygonss
        """
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
        if ((edge1.twin.origin != edge2.origin and
            get_direction(edge1.twin.prev.origin, edge1.twin.origin, edge2.origin) != Direction.LEFT and
            get_direction(edge1.twin.origin, edge2.origin, edge2.twin.next.twin.origin) != Direction.LEFT or
            edge1.twin.origin == edge2.origin and
            get_direction(edge1.twin.prev.origin, edge2.origin, edge2.twin.next.twin.origin) != Direction.LEFT
            ) and
            (edge2.twin.origin != edge1.origin and
            get_direction(edge2.twin.prev.origin, edge2.twin.origin, edge1.origin) != Direction.LEFT and
            get_direction(edge2.twin.origin, edge1.origin, edge1.twin.next.twin.origin) != Direction.LEFT or
            edge2.twin.origin == edge1.origin and
            get_direction(edge2.twin.prev.origin, edge1.origin, edge1.twin.next.twin.origin) != Direction.LEFT
            )):
            return True
        else:
            return False

    def merge(edge1, edge2):
        """
        Merges the faces edge1.twin.incident_face and edge2.twin.incident_face, adding edges if necessary
        """
        if edge1.twin.origin != edge2.origin:
            h1 = HalfEdge(edge1.twin.origin)
            h2 = HalfEdge(edge2.origin)
            h1.twin = h2
            h2.twin = h1

            h1.prev = edge1.twin.prev
            edge1.twin.prev.next = h1
            h1.next = edge2.twin.next
            edge2.twin.next.prev = h1
            h2.incident_face = dummy_face
        else:
            edge1.twin.prev.next = edge2.twin.next
            edge2.twin.next.prev = edge1.twin.prev

        if edge2.twin.origin != edge1.origin:
            h3 = HalfEdge(edge2.twin.origin)
            h4 = HalfEdge(edge1.origin)
            h3.twin = h4
            h4.twin = h3

            h3.prev = edge2.twin.prev
            edge2.twin.prev.next = h3
            h3.next = edge1.twin.next
            edge1.twin.next.prev = h3
            h4.incident_face = dummy_face
        else:
            edge2.twin.prev.next = edge1.twin.next
            edge1.twin.next.prev = edge2.twin.prev

        # Merge the faces into one
        edge = edge1.twin.prev.next
        while edge.incident_face != edge1.twin.incident_face:
            edge.incident_face = edge1.twin.incident_face
            edge = edge.next
        edge.incident_face.outer_component = edge
        dcel.faces.remove(edge2.twin.incident_face)

        # Update the incident faces of the twins such that we can not merge them again
        edge1.twin.incident_face = dummy_face
        edge2.twin.incident_face = dummy_face


    did_merge = True
    while did_merge:
        did_merge = False
        for face in dcel.interior_faces():
            did_merge = merge_neighbouring_faces(face)
            if did_merge:
                break


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


