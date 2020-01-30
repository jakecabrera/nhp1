from nhp1.datastructures.routingTable import RoutingTable
from nhp1.datastructures.stack import Stack

# Class to control which trucks get what packages and what routes to take
class Dispatch():
  # Constructor for Dispatch class
  def __init__(self):
    self.trucks = []
    self.routing_table = RoutingTable()
    self.packages = []
    self.undelivered_packages = Stack()

  # Sort packages, first by delivery time, then by distance to hub
  def sort_packages(self):
    pass

  # pick a set of packages to load evenly on to the available trucks
  def load_trucks(self):
    # Load the trucks until full in a round-robin style to evenly split the load
    full_trucks = 0
    while full_trucks < len(self.trucks):
      for truck in self.trucks:
        if len(truck.deliverables) == truck.MAX_DELIVERABLES: full_trucks += 1
        # TODO: choose packages to put on the truck and create a route from those (don't forget complications)
    pass
