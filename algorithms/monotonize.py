from datastructures.dcel import *
from datastructures.edgebst import *


def monotonize_polygon(dcel: DCEL, verbose=False):
    """
    Subdivides the input polygon into y-monotone regions by inserting edges.
    """

    def handle_vertex(vertex: Vertex, status):
        if vertex.type == VertexType.START:
            # we state the left edge is the incident edge because of the counter clock wise rotation.
            status = status.insert(vertex.incident_half_edge, vertex.y)
            vertex.incident_half_edge.helper = vertex
            vertex.incident_half_edge.twin.helper = vertex

        if vertex.type == VertexType.END:
            # we state the left edge is the prev of incident edge because of the counter clock wise rotation.
            edge = vertex.incident_half_edge.prev
            if edge.helper and edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge.helper, vertex)
            status = status.delete(edge, vertex.y)

        if vertex.type == VertexType.SPLIT:
            edge = status.range_query(rat(vertex.x), vertex.y)[0]
            dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex
            edge.helper.twin = vertex
            right_edge = vertex.incident_half_edge
            status = status.insert(right_edge, vertex.y)
            right_edge.helper = vertex
            right_edge.twin.helper = vertex

        if vertex.type == VertexType.MERGE:
            right_edge = vertex.incident_half_edge.prev
            if right_edge.helper and right_edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(right_edge.helper, vertex)
            status = status.delete(right_edge, vertex.y)
            edge_prime = status.range_query(rat(vertex.x), vertex.y)[0]
            if edge_prime.helper and edge_prime.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge_prime.helper, vertex)
            edge_prime.helper = vertex
            edge_prime.twin.helper = vertex

        if vertex.type == VertexType.REGULAR_RIGHT:
            if (vertex.incident_half_edge.twin.origin.y > vertex.y or
                vertex.incident_half_edge.twin.origin.y == vertex.y and
                    vertex.incident_half_edge.twin.origin.x < vertex.x):
                upper_edge = vertex.incident_half_edge
                lower_edge = vertex.incident_half_edge.prev
            else:
                upper_edge = vertex.incident_half_edge.prev
                lower_edge = vertex.incident_half_edge
            if upper_edge.helper and upper_edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(upper_edge.helper, vertex)
            status = status.delete(upper_edge, vertex.y)
            status = status.insert(lower_edge, vertex.y)
            lower_edge.helper = vertex

        if vertex.type == VertexType.REGULAR_LEFT:
            edge = status.range_query(rat(vertex.x), vertex.y)[0]
            if edge.helper and edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex

        return status
    if verbose:
        print("Subdividing the polygon into y-monotone pieces...")
    vertices = dcel.vertices
    vertices.sort(key=lambda coordinate: (-coordinate.y, coordinate.x))
    status = EdgebstNode()
    for i in range(len(vertices)):
        vertex = vertices[i]
        status = handle_vertex(vertex, status)

    # Now that we're finished editing the DCEL we can recompute  the faces
    if verbose:
        print("Finished subdividing the polygon into y-monotone pieces.")
    dcel.recompute_faces()

    return dcel
