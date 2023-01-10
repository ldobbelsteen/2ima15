import Rationals as rat

def slope(edge):
    rat(edge.twin.origin.x - edge.origin.x, edge.twin.origin.y - edge.origin.y)

def edgeSmaller(edge1,edge2,y):
    xEdge1 = rat(edge1.origin.x) + slope(edge1) * rat(y-edge1.origin.y)
    xEdge2 = rat(edge2.origin.x) + slope(edge2) * rat(y-edge2.origin.y)
    return xEdge1 < xEdge2

def leftOfVertex(edge,vertex):
    xEdge = rat(edge.origin.x) + slope(edge) * rat(vertex.y-edge.origin.y)
    return xEdge < vertex.x 


class EdgebstNode:
    def __init__(self, val=None):
        self.left = None
        self.right = None
        self.val = val

    def insert(self, val,y):
        if not self.val:
            self.val = val
            return

        if self.val == val:
            return

        if edgeSmaller(val, self.val, y):
            if self.left:
                self.left.insert(val)
                return
            self.left = EdgebstNode(val)
            return

        if self.right:
            self.right.insert(val)
            return
        self.right = EdgebstNode(val)

    def delete(self, val,y):
        if self == None:
            return self
        if edgeSmaller(val,self.val, y):
            if self.left:
                self.left = self.left.delete(val)
            return self
        if not edgeSmaller(val,self.val, y) and val != self.val:
            if self.right:
                self.right = self.right.delete(val)
            return self
        if self.right == None:
            return self.left
        if self.left == None:
            return self.right
        min_larger_node = self.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left
        self.val = min_larger_node.val
        self.right = self.right.delete(min_larger_node.val)
        return self
    
    def leftEdgeFinder(self, vertex):
        if leftOfVertex(self.val, vertex):
            if leftOfVertex(self.right,vertex):
                return self.leftEdgeFinder(self.right, vertex)
            else:
                return self.val
        else:
            return self.leftEdgeFinder(self.left,vertex)