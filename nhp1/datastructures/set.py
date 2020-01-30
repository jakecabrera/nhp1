from nhp1.datastructures.bst import BSTIterator, BSTNode


class Set:
  def __init__(self, get_key_function=None):
    self.storage_root = None
    if get_key_function is None:
      # By default, the key of an element is itself
      self.get_key = lambda el: el
    else:
      self.get_key = get_key_function

  def __iter__(self):
    if self.storage_root is None:
      return BSTIterator(None)
    minNode = self.storage_root
    while minNode.left is not None:
      minNode = minNode.left
    return BSTIterator(minNode)

  def add(self, new_element):
    new_elementKey = self.get_key(new_element)
    if self.node_search(new_elementKey) is not None:
      return False

    newNode = BSTNode(new_element, None)
    if self.storage_root is None:
      self.storage_root = newNode
    else:
      node = self.storage_root
      while node is not None:
        if new_elementKey < self.get_key(node.data):
          # Go left
          if node.left:
            node = node.left
          else:
            node.left = newNode
            newNode.parent = node
            return True
        else:
          # Go right
          if node.right:
            node = node.right
          else:
            node.right = newNode
            newNode.parent = node
            return True

  def difference(self, other_set):
    result = Set(self.get_key)
    for element in self:
      if other_set.search(self.get_key(element)) is None:
        result.add(element)
    return result

  def filter(self, predicate):
    result = Set(self.get_key)
    for element in self:
      if predicate(element):
        result.add(element)
    return result

  def intersection(self, other_set):
    result = Set(self.get_key)
    for element in self:
      if other_set.search(self.get_key(element)) is not None:
        result.add(element)
    return result

  def __len__(self):
    if self.storage_root is None:
      return 0
    return self.storage_root.count()

  def map(self, map_function):
    result = Set(self.get_key)
    for element in self:
      new_element = map_function(element)
      result.add(new_element)
    return result

  def node_search(self, key):
    # Search the BST
    node = self.storage_root
    while node is not None:
      # Get the node's key
      node_key = self.get_key(node.data)

      # Compare against the search key
      if node_key == key:
        return node
      elif key > node_key:
        node = node.right
      else:
        node = node.left
    return node

  def remove(self, key):
    self.remove_node(self.node_search(key))

  def remove_node(self, node_to_remove):
    if node_to_remove is not None:
      # Case 1: Internal node with 2 children
      if node_to_remove.left is not None and node_to_remove.right is not None:
        successor = node_to_remove.get_successor()

        # Copy the data value from the successor
        dataCopy = successor.data

        # Remove successor
        self.remove_node(successor)

        # Replace node_to_remove's data with successor data
        node_to_remove.data = dataCopy

      # Case 2: Root node (with 1 or 0 children)
      elif node_to_remove is self.storage_root:
        if node_to_remove.left is not None:
          self.storage_root = node_to_remove.left
        else:
          self.storage_root = node_to_remove.right

        if self.storage_root:
          self.storage_root.parent = None

      # Case 3: Internal node with left child only
      elif node_to_remove.left is not None:
        node_to_remove.parent.replace_child(node_to_remove, node_to_remove.left)

      # Case 4: Internal node with right child only, or leaf node
      else:
        node_to_remove.parent.replace_child(node_to_remove, node_to_remove.right)

  def search(self, key):
    # Search the BST
    node = self.node_search(key)
    if node is not None:
      return node.data
    return None

  def union(self, other_set):
    result = Set(self.get_key)
    for element in self:
      result.add(element)
    for element in other_set:
      result.add(element)
    return result
