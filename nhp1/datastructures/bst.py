class BSTNode:
  def __init__(self, data, parent, left=None, right=None):
    self.data = data
    self.left = left
    self.right = right
    self.parent = parent

  def count(self):
    leftCount = 0
    rightCount = 0
    if self.left is not None:
      leftCount = self.left.count()
    if self.right is not None:
      rightCount = self.right.count()
    return 1 + leftCount + rightCount

  def get_successor(self):
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

  def replace_child(self, current_child, new_child):
    if current_child is self.left:
      self.left = new_child
      if self.left:
        self.left.parent = self
    elif current_child is self.right:
      self.right = new_child
      if self.right:
        self.right.parent = self


class BSTIterator:
  def __init__(self, node):
    self.node = node

  # For Python versions >= 3
  def __next__(self):
    return self.next()

  # For Python versions < 3
  def next(self):
    if self.node is None:
      raise StopIteration
    else:
      current = self.node.data
      self.node = self.node.get_successor()
      return current
