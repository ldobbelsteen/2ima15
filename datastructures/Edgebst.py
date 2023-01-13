from datastructures.Rationals import Rationals as rat

def slope(edge):
    return rat(edge.twin.origin.y - edge.origin.y, edge.twin.origin.x - edge.origin.x)

def xOfEdge(edge, y):
    # If edge is vertical:
    if edge.origin.x == edge.twin.origin.x:
        return rat(edge.origin.x)
    # Edge is horizontal:
    elif edge.origin.y == edge.twin.origin.y:
    # Edge is not horizontal nor vertical:
        return rat(max(edge.origin.x, edge.twin.origin.x)) # TODO: I don't know if this is correct
    else:
        b = rat(edge.origin.y) - slope(edge) * rat(edge.origin.x)
        xEdge = (rat(y) - b) / slope(edge)
        return xEdge

def edgeSmaller(edge1,edge2,y):
    xEdge1 = xOfEdge(edge1, y)
    xEdge2 = xOfEdge(edge2, y)
    return xEdge1 < xEdge2

def leftOfVertex(edge,vertex):
    return xOfEdge(edge, vertex.y) < rat(vertex.x) 


class EdgebstNode:
    def __init__(self, val=None):
        self.left = None
        self.right = None
        self.val = val

    def insert(self, val, y):
        if not self.val:
            self.val = val
            return

        if self.val == val:
            return

        if edgeSmaller(val, self.val, y):
            if self.left:
                self.left.insert(val, y)
                return
            self.left = EdgebstNode(val)
            return

        if self.right:
            self.right.insert(val, y)
            return
        self.right = EdgebstNode(val)

    def delete(self, val, y):
        if self == None:
            return self
        if edgeSmaller(val,self.val, y):
            if self.left:
                self.left = self.left.delete(val, y)
            return self
        if not edgeSmaller(val,self.val, y) and val != self.val and val != self.val.twin: # TSET
            if self.right:
                self.right = self.right.delete(val, y)
            return self
        if self.right == None:
            return self.left
        if self.left == None:
            return self.right
        min_larger_node = self.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left
        self.val = min_larger_node.val
        self.right = self.right.delete(min_larger_node.val, y)
        return self
    
    def leftEdgeFinder(self, vertex):
        if leftOfVertex(self.val, vertex):
            if self.right and leftOfVertex(self.right.val, vertex):
                return self.right.leftEdgeFinder(vertex)
            else:
                return self.val
        else:
            return self.left.leftEdgeFinder(vertex)
    
