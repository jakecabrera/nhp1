# Data structure to hold all the locations and the distances between them
class RoutingTable():
  # Constructor for RoutingTable class
  def __init__(self, addresses, distance_matrix):
    self.destinations = addresses
    self.distance_matrix = distance_matrix
    self.routing_matrix = []
    
  # lookup the distance between two addresses
  def distance_between(self, a, b):
    if len(self.distance_matrix) == 0: return 0.0
    return self.distance_matrix[self.destinations.index(a)][self.destinations.index(b)]

  # lookup distance to the hub
  def distance_to_hub(self, a):
    return self.distance_matrix[self.destinations.index(a)][0]

  # Created a routing table which is each address with a list of addresses sorted by distance
  def build_routing_matrix(self):
    for i, distances in enumerate(self.distance_matrix):
      # Pair the distance with the address associated for this record
      distances = [(self.destinations[i], d) for i, d in enumerate(distances)]
      distances.sort(key= lambda x: (x[1], x[0].zip, x[0].address))
      self.routing_matrix.append(distances)

  # return the routing matrix record for the address specified
  def get_routing_record(self, address): # O(n)
    i = self.destinations.index(address) # O(n)
    return self.routing_matrix[i]
