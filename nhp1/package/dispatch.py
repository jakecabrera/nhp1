from nhp1.datastructures.routingTable import RoutingTable
from nhp1.datastructures.stack import Stack
from nhp1.datastructures.hashTable import ChainingHashTable
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.controller import Controller
from nhp1.package.deliverable import Deliverable

# Class to control which trucks get what packages and what routes to take
class Dispatch():
  # Constructor for Dispatch class
  def __init__(self, context: Controller):
    self.trucks = []
    self.sorted_routes = ChainingHashTable()
    self.context = context

    # Build the routing table
    d = DistanceReader('resources/WGUPS Distance Table.csv')
    d.load()
    self.routing_table = RoutingTable(d.addresses, d.distance_matrix)
    self.routing_table.build_routing_matrix()

    # Build the packages list
    p = PackageReader('resources/WGUPS Package File.csv')
    p.load()
    self.packages = p.packages
    self.all_packages = list(p.packages)

  # Sort packages, first by delivery time, then by distance to hub
  def sort_packages(self):
    def package_sort(p: Deliverable):
      complication = 0
      deliverable_req = 1
      if p.complication is not None:
        if p.complication.delay is not None and self.context.now < p.complication.delay:
         complication = 1
        if len(p.complication.deliverable_req) > 0:
          deliverable_req = 0
      deadline = p.deadline
      distance = self.routing_table.distance_to_hub(p.address)
      return complication, deadline, deliverable_req, distance
    self.packages.sort(key=package_sort)

  # pick a set of packages to load evenly on to the available trucks
  def load_trucks(self):
    # Load the trucks until full in a round-robin style to evenly split the load
    full_trucks = []
    while len(full_trucks) < len(self.trucks):
      for truck in self.trucks:
        if len(truck.deliverables) == truck.MAX_DELIVERABLES:
          if truck not in full_trucks: full_trucks.append(truck)
          continue
        # TODO: choose packages to put on the truck and create a route from those (don't forget complications)
        # Now do logic to load the trucks
        # Recursive function to get a list of all required packages
        def get_required_packages(package: Deliverable, known=[]):
          required_packages = []
          if package.status == 'at hub':
            required_packages = [package]
            known += package.id
          if package.complication is None: return required_packages
          if len(package.complication.deliverable_req) == 0: return required_packages
          for req in package.complication.deliverable_req:
            if req in known: continue
            req_package = self.all_packages[req-1]
            required_packages.extend(get_required_packages(req_package))
          return required_packages
        # TODO: figure out why im getting duplicates
        packages_to_load = get_required_packages(self.packages[0])
        print(len(packages_to_load))
        for p in packages_to_load:
          print(p)
          truck.deliverables.append(p)
        for p in packages_to_load:
          self.packages.remove(p)

    pass
