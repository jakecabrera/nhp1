from nhp1.datastructures.bst import BSTIterator, BSTNode


# like a list but only unique entries
class Set:
  # constructor of the Set class
  def __init__(self, get_key_function=None):
    self.storage_root = None
    if get_key_function is None:
      # By default, the key of an element is itself
      self.get_key = lambda el: el
    else:
      self.get_key = get_key_function

  # so that you can use Set in a for loop
  def __iter__(self): # avg O(logn) worst O(n)
    if self.storage_root is None:
      return BSTIterator(None)
    minNode = self.storage_root
    while minNode.left is not None:
      minNode = minNode.left
    return BSTIterator(minNode)

  # add an element to the set. If it already exists, don't do anything
  # return whether an element was added or not
  def add(self, new_element): # avg O(logn) worst O(n)
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

  # add all elements of an iterable to the set
  def add_all(self, elements):
    for element in elements:
      self.add(element)

  # Remove any elements in other_set from self
  def difference(self, other_set): # O(n)
    result = Set(self.get_key)
    for element in self:
      if other_set.search(self.get_key(element)) is None:
        result.add(element)
    return result

  # remove any elements that don't return true when predicate is used on it
  def filter(self, predicate): # O(n)
    result = Set(self.get_key)
    for element in self:
      if predicate(element):
        result.add(element)
    return result

  # return only elements found in both lists
  def intersection(self, other_set): # O(n^2)
    result = Set(self.get_key)
    for element in self:
      if other_set.search(self.get_key(element)) is not None:
        result.add(element)
    return result

  # makes it so you can use len() on this class
  def __len__(self): # O(1)
    if self.storage_root is None:
      return 0
    return self.storage_root.count()

  # applies map_function to every element in the list
  def map(self, map_function): # O(nlogn)
    result = Set(self.get_key)
    for element in self:
      new_element = map_function(element)
      result.add(new_element)
    return result

  # return node that matches key or None if no matches
  def node_search(self, key): # avg O(logn) worst O(n)
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

  # remove a node by its key
  def remove(self, key): # O((logn)^2)
    self.remove_node(self.node_search(key))

  # remove the node and adjust BST as necessary
  def remove_node(self, node_to_remove): # O(logn)
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

  # return data of the node that matches the key
  def search(self, key): # avg O(logn) worst O(n)
    # Search the BST
    node = self.node_search(key)
    if node is not None:
      return node.data
    return None

  # Override in operator
  def __contains__(self, item):
    return self.search(item) is not None

  # combines two sets without duplicates
  def union(self, other_set): # O(n)
    result = Set(self.get_key)
    for element in self:
      result.add(element)
    for element in other_set:
      result.add(element)
    return result
