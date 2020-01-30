# Data structure to hold all the locations and the distances between them
class RoutingTable():
  # Constructor for RoutingTable class
  def __init__(self):
    self.destinations = []
    self.distance_matrix = []

  # lookup the distance between two addresses
  def distance_between(self, a, b):
    if len(self.distance_matrix) == 0: return 0.0
    return self.distance_matrix[self.destinations.index(a)][self.destinations.index(b)]
