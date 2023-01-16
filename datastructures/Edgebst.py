from datastructures.Rationals import Rationals as rat

def slope(edge):
    return rat(edge.twin.origin.y - edge.origin.y, edge.twin.origin.x - edge.origin.x)

def x_of_edge(edge, y):
    # If edge is vertical:
    if edge.origin.x == edge.twin.origin.x:
        return rat(edge.origin.x)
    # Edge is horizontal:
    elif edge.origin.y == edge.twin.origin.y:
        return rat(max(edge.origin.x, edge.twin.origin.x))
    # Edge is not horizontal nor vertical:
    else:
        b = rat(edge.origin.y) - slope(edge) * rat(edge.origin.x)
        x_edge = (rat(y) - b) / slope(edge)
        return x_edge

def edge_smaller(edge1,edge2,y):
    x_edge1 = x_of_edge(edge1, y)
    x_edge2 = x_of_edge(edge2, y)
    return x_edge1 < x_edge2


class EdgebstNode:
    def __init__(self, val=None, right_end=None):
        self.left = None
        self.right = None
        self.val = val
        self.right_end = right_end

    def insert_interval(self, val, right_end, y):
        if not self.val:
            self.val = val
            self.right_end = right_end
            return

        if self.val == val or self.val == self.val.twin:
            return

        if edge_smaller(val, self.val, y):
            if self.left:
                self.left.insert_interval(val, right_end, y)
                return
            self.left = EdgebstNode(val, right_end)
            return

        if self.right:
            self.right.insert_interval(val, right_end, y)
            return
        self.right = EdgebstNode(val, right_end)

    def delete_subfunction(self, val, y):
        if self == None:
            return self
        # Element is located in left subtree
        if edge_smaller(val, self.val, y):
            if self.left:
                self.left = self.left.delete_subfunction(val, y)
            return self
        # Element is locate in right subtree
        if not edge_smaller(val, self.val, y) and val != self.val and val != self.val.twin:
            if self.right:
                self.right = self.right.delete_subfunction(val, y)
            return self
        # Current element should be deleted
        if self.right == None:
            return self.left
        if self.left == None:
            return self.right
        min_larger_node = self.right
        while min_larger_node.left:
            min_larger_node = min_larger_node.left
        self.val = min_larger_node.val
        self.right_end = min_larger_node.right_end
        self.right = self.right.delete_subfunction(min_larger_node.val, y)
        return self

    def range_query(self, x, y):
        """
        returns a tuple consisting of the endpoints of the range in which the querypoint is contained
        """
        if not self.val:
            return None
        if x_of_edge(self.val, y) < x and (not self.right_end or x < x_of_edge(self.right_end, y)):
            return (self.val, self.right_end)
        if x_of_edge(self.val, y) > x:
            if self.left:
                return self.left.range_query(x, y)
            else:
                # The query point lies left of the leftmost interval
                return None
        if x_of_edge(self.right_end, y) < x:
            return self.right.range_query(x, y)
        
    def right_end_query(self, val, y):
        """
        given the left end of an interval, returns the right end of that interval
        """
        if self.val == val or self.val == val.twin:
            return self.right_end
        if x_of_edge(self.val, y) > x_of_edge(val, y):
            return self.left.right_end_query(val, y)
        if x_of_edge(self.val, y) < x_of_edge(val, y):
            return self.right.right_end_query(val, y)
    
    def left_end_query(self, right_end, y):
        """
        given the right end of an interval, returns the left end of that interval
        """
        if self.right_end == right_end or self.right_end == right_end.twin:
            return self.val
        if not self.right_end or x_of_edge(self.right_end, y) > x_of_edge(right_end, y):
            if not self.left:
                return None
            return self.left.left_end_query(right_end, y)
        if x_of_edge(self.right_end, y) < x_of_edge(right_end, y):
            return self.right.left_end_query(right_end, y)

    def get_left_most_edge(self):
        if not self.left:
            return self.val
        else:
            return self.left.get_left_most_edge()

    def insert(self, val, y):
        """
        Inserts a new edge into the tree by first querying the interval this new edge is contained in
        (which will now be rightbounded by the newly inserted edge) and replacing it with the two new
        intervals.
        """
        if self.val == None:
            self.insert_interval(val, None, y)
            return self
        else:
            # First query the interval in which the new edge is contained
            interval = self.range_query(x_of_edge(val, y), y)
            if not interval:
                # The edge we are inserting is the leftmost edge, i.e. it is not contained in any existing intervals
                right_end = self.get_left_most_edge()
                self.insert_interval(val, right_end, y)
                return self
            else:
                old_val, old_right_end = interval
                # Delete the interval from the tree and replace it with two new ones
                t = self.delete_subfunction(old_val, y)
                if not t:
                    t = EdgebstNode()
                t.insert_interval(old_val, val, y)
                t.insert_interval(val, old_right_end, y)
                return t

    def delete(self, val, y):
        """
        Deletes an edge from the tree. If there was an interval left of the deleted edge it extends,
        hence we replace this interval with the updated one.
        """
        # Find right end of interval being deleted
        right_end = self.right_end_query(val, y)
        # Find left edge of interval whose left end now changed and replace it
        left_end = self.left_end_query(val, y)
        if not left_end:
            # Interval deleted was leftmost interval, no interval to replace
            t = self.delete_subfunction(val, y)
            if not t:
                t = EdgebstNode()
            return t
        else:
            # Delete the edge that we want to delete
            t = self.delete_subfunction(val, y)
            # Replace the edge that changed because of the deletion
            t = t.delete_subfunction(left_end, y)
            if not t:
                t = EdgebstNode()
            t.insert_interval(left_end, right_end, y)
            return t


    
    # ===== DEBUGGING FUNCTIONS =============================================

    def print_nodes(self):
        if not self.val:
            return
        print(f"left: (({self.val.origin.x}, {self.val.origin.y}), ({self.val.twin.origin.x}, {self.val.twin.origin.y}))")
        if self.right_end:
            print(f"right: (({self.right_end.origin.x}, {self.right_end.origin.y}), ({self.right_end.twin.origin.x}, {self.right_end.twin.origin.y}))")
        else:
            print("right: None")
        if self.left:
            self.left.print_nodes()
        if self.right:
            self.right.print_nodes()

    def nodes_to_string(self):
        if not self.val:
            return
        str_rep = f"(({self.val.origin.x}, {self.val.origin.y}), ({self.val.twin.origin.x}, {self.val.twin.origin.y}))"
        if self.left:
            str_rep = str_rep + " : (left: " + self.left.nodes_to_string()
        else:
            str_rep = str_rep + "(left: ()"
        if self.right:
            str_rep = str_rep + "right: " + self.right.nodes_to_string() +")"
        else:
            str_rep = str_rep + "right ())"
        return str_rep
    
    def node_count(self):
        count = 0
        if self.left:
            count += self.left.node_count()
        if self.right:
            count += self.right.node_count()
        return count

    def is_valid_bst_val(self, y):
        valid = True
        if self.left:
            valid = (valid and self.left.is_valid_bst_val(y) and 
                     x_of_edge(self.left.val, y) < x_of_edge(self.val, y))
        if self.right:
            valid = (valid and self.right.is_valid_bst_val(y) and
                     x_of_edge(self.right.val, y) > x_of_edge(self.val, y))
        return valid
    
    def is_valid_bst_right_end(self, y):
        valid = True
        if self.left:
            valid = (valid and self.left.is_valid_bst_right_end(y) and 
                     (not self.right_end or x_of_edge (self.left.right_end, y) < x_of_edge(self.right_end, y)))
        if self.right:
            valid = (valid and self.right.is_valid_bst_right_end(y) and 
                     (not self.right.right_end or x_of_edge(self.right.right_end, y) > x_of_edge(self.right_end, y)))
        return valid

    def exists_right_none(self):
        exists = True
        if self.right_end:
            exists = False
        if self.right:
            exists = exists or self.right.exists_right_none()
        if self.left:
            exists = exists or self.left.exists_right_none()
        return exists
