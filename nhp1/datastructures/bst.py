class BSTNode:
  def __init__(self, data, parent, left=None, right=None):
    self.data = data
    self.left = left
    self.right = right
    self.parent = parent

  def count(self): # O(n)
    leftCount = 0
    rightCount = 0
    if self.left is not None:
      leftCount = self.left.count()
    if self.right is not None:
      rightCount = self.right.count()
    return 1 + leftCount + rightCount

  def get_successor(self): # avg O(logn) worst O(n)
    # Successor resides in right subtree, if present
    if self.right is not None:
      successor = self.right
      while successor.left is not None:
        successor = successor.left
      return successor

    # Otherwise the successor is up the tree
    # Traverse up the tree until a parent is encountered from the left
    node = self
    while node.parent is not None and node == node.parent.right:
      node = node.parent
    return node.parent

  # Replace the specified child of a node with a new child
  def replace_child(self, current_child, new_child): # O(1)
    if current_child is self.left:
      self.left = new_child
      if self.left:
        self.left.parent = self
    elif current_child is self.right:
      self.right = new_child
      if self.right:
        self.right.parent = self


# Iterator used to iterate over a BST
class BSTIterator:
  def __init__(self, node):
    self.node = node

  # Iterator method to access next element
  def __next__(self):
    return self.next()
