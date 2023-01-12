import sys
sys.path.insert(0,"..")
from datastructures.Edgebst import *
from datastructures.DCEL import *


def makeMonotone(dcel: DCEL):
    def handleVertex(vertex: Vertex):
        if vertex.type == VertexType.START:
            # we state the left edge is the incident edge because of the counter clock wise rotation.
            status.insert(vertex.incident_half_edge,vertex.y)
            vertex.incident_half_edge.helper = vertex
            vertex.incident_half_edge.twin.helper = vertex
        if vertex.type == VertexType.END:
             # we state the left edge is the prev of incident edge because of the counter clock wise rotation.
            edge = vertex.incident_half_edge.prev
            if edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge.helper, vertex)
            status.delete(edge,vertex.y)
        if vertex.type == VertexType.SPLIT:
            edge = status.leftEdgeFinder(vertex)
            dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex
            edge.helper.twin = vertex
            rightEdge = vertex.incident_half_edge
            status.insert(rightEdge, vertex.y)
            rightEdge.helper = vertex
            rightEdge.twin.helper = vertex
        if vertex.type == VertexType.MERGE:
            rightEdge = vertex.incident_half_edge.prev
            if rightEdge.helper.type == VertexType.MERGE:
                dcel.insert_edge(rightEdge.helper, vertex)
            status.delete(rightEdge, vertex.y)
            edgePrime = status.leftEdgeFinder(vertex)
            if edgePrime.helper.type == VertexType.MERGE:
                dcel.insert_edge(edgePrime.helper, vertex)
            edgePrime.helper = vertex
            edgePrime.twin.helper = vertex
        if vertex.type == VertexType.REGULAR_RIGHT:
            # if vertex.incident_half_edge.twin.origin.y >= vertex.y:
            #     upperEdge = vertex.incident_half_edge
            #     lowerEdge = vertex.incident_half_edge.twin
            # else:
            #     upperEdge = vertex.incident_half_edge.twin
            #     lowerEdge = vertex.incident_half_edge
            upperEdge = vertex.incident_half_edge.prev
            lowerEdge = vertex.incident_half_edge
            if upperEdge.helper.type == VertexType.MERGE:
                dcel.insert_edge(upperEdge.helper, vertex)
            status.delete(upperEdge,vertex.y)
            status.insert(lowerEdge,vertex.y)
            lowerEdge.helper = vertex
        if vertex.type == VertexType.REGULAR_LEFT:
            edge = status.leftEdgeFinder(vertex)
            if edge.helper.type == VertexType.MERGE:
                dcel.insert_edge(edge.helper, vertex)
            edge.helper = vertex  

    vertices = dcel.vertices 
    vertices.sort(key=lambda coordinate: (coordinate.y, coordinate.x))
    status = EdgebstNode()
    while len(vertices) != 0:
        vertex = vertices.pop()
        print(vertex.x, vertex.y)
        handleVertex(vertex)
    return dcel 


