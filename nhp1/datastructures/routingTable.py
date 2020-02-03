from nhp1.datastructures.set import Set

# Data structure to hold all the locations and the distances between them
class RoutingTable():
  # Constructor for RoutingTable class
  def __init__(self, addresses, distance_matrix): # O(1)
    self.destinations = addresses
    self.distance_matrix = distance_matrix
    self.routing_matrix = []
    
  # lookup the distance between two addresses
  def distance_between(self, a, b): # O(addresses^2)
    if len(self.distance_matrix) == 0: return 0.0
    return self.distance_matrix[self.destinations.index(a)][self.destinations.index(b)]

  # lookup distance to the hub
  def distance_to_hub(self, a): # O(addresses)
    return self.distance_matrix[self.destinations.index(a)][0]

  # Created a routing table which is each address with a list of addresses sorted by distance
  def build_routing_matrix(self, useable_addresses): # O((addresses^2)*log(addresses))
    # narrow down which indexes we are concerned about
    self.destinations = [self.destinations[0]] + useable_addresses # Because we also want the hub
    useable_addresses = self.destinations
    useable_indexes = []
    for i in range(len(self.destinations)):
      if self.destinations[i] in useable_addresses:
        useable_indexes.append(i)

    # cut out entire record for addresses we don't care about
    self.distance_matrix = [r[1] for r in list(filter(lambda r: r[0] in useable_indexes, enumerate(self.distance_matrix)))]

    # trim each record to only contain destinations we care about
    for i in range(len(self.distance_matrix)):
      record = self.distance_matrix[i]
      self.distance_matrix[i] = [d[1] for d in list(filter(lambda d: d[0] in useable_indexes, enumerate(record)))]

    for i, distances in enumerate(self.distance_matrix): # O((addresses^2)*log(addresses))
      # Pair the distance with the address associated for this record
      distances = [(self.destinations[i], d) for i, d in enumerate(distances)]
      distances.sort(key= lambda x: (x[1], x[0].zip, x[0].address)) # O(addresses*log(addresses))
      self.routing_matrix.append(distances)

  # return the routing matrix record for the address specified
  def get_routing_record(self, address): # O(n)
    i = self.destinations.index(address) # O(n)
    return self.routing_matrix[i]
