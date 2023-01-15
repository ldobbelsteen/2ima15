import sys
sys.path.insert(0,"..")
from datastructures.Edgebst import *
from datastructures.DCEL import *


def makeMonotone(dcel: DCEL):
    def handleVertex(vertex: Vertex, status):
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
            status = status.delete(edge,vertex.y)

        if vertex.type == VertexType.SPLIT:
            edge = status.range_query(rat(vertex.x), vertex.y)[0]
            dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex
            edge.helper.twin = vertex
            rightEdge = vertex.incident_half_edge
            status = status.insert(rightEdge, vertex.y)
            rightEdge.helper = vertex
            rightEdge.twin.helper = vertex

        if vertex.type == VertexType.MERGE:
            rightEdge = vertex.incident_half_edge.prev
            if rightEdge.helper and rightEdge.helper.type == VertexType.MERGE:
                dcel.insert_edge(rightEdge.helper, vertex)
            status = status.delete(rightEdge, vertex.y)
            edgePrime = status.range_query(rat(vertex.x), vertex.y)[0]
            if edgePrime.helper and edgePrime.helper.type == VertexType.MERGE:
                dcel.insert_edge(edgePrime.helper, vertex)
            edgePrime.helper = vertex
            edgePrime.twin.helper = vertex

        if vertex.type == VertexType.REGULAR_RIGHT:
            if (vertex.incident_half_edge.twin.origin.y > vertex.y or
                vertex.incident_half_edge.twin.origin.y == vertex.y and
                vertex.incident_half_edge.twin.origin.x > vertex.x):
                upperEdge = vertex.incident_half_edge
                lowerEdge = vertex.incident_half_edge.prev
            else:
                upperEdge = vertex.incident_half_edge.prev
                lowerEdge = vertex.incident_half_edge
            if upperEdge.helper and upperEdge.helper.type == VertexType.MERGE:
                dcel.insert_edge(upperEdge.helper, vertex)
            status = status.delete(upperEdge,vertex.y)
            status = status.insert(lowerEdge,vertex.y)
            lowerEdge.helper = vertex

        if vertex.type == VertexType.REGULAR_LEFT:
            edge = status.range_query(rat(vertex.x), vertex.y)[0]
            if edge.helper and edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex
        
        return status

    vertices = dcel.vertices 
    vertices.sort(key=lambda coordinate: (-coordinate.y, coordinate.x))
    status = EdgebstNode()
    for i in range(len(vertices)):
        vertex = vertices[i]
        status = handleVertex(vertex, status)
    return dcel 


