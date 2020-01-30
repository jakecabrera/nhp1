# my own implementation of a stack datastructure
class Stack():
  # constructor for the Stack class
  def __init__(self):
    self.top = None
    pass

  # Add an object to the stack
  def add(self, obj):
    obj.below = self.top
    self.top = obj

  # Pop the top of the stack off and return it
  def pop(self):
    if self.top is None:
      return None
    result = self.top.value
    self.top = self.top.below
    return result

# a node for each element in the stack
class StackNode():
  # constructor for the StackNode class
  def __init__(self):
    self.value = None
    self.below = None