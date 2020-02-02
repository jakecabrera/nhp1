from nhp1.datastructures.routingTable import RoutingTable
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.controller import Controller
from nhp1.package.deliverable import Deliverable
from nhp1.package.truck import Truck
from nhp1.package.address import Address
from nhp1.datastructures.hashTable import PackageHashTable
from nhp1.datastructures.set import Set

# Class to control which trucks get what packages and what routes to take
class Dispatch():
  # Constructor for Dispatch class
  def __init__(self, context: Controller):
    self.trucks = []
    self.context = context
    self.home = Address('HUB (84107)')

    # Build the routing table
    d = DistanceReader('resources/WGUPS Distance Table.csv')
    d.load()
    self.routing_table = RoutingTable(d.addresses, d.distance_matrix)
    self.routing_table.build_routing_matrix()

    # Build the packages list
    p = PackageReader('resources/WGUPS Package File.csv')
    p.load()
    self.packages = p.packages
    self.all_packages = PackageHashTable(initial_capacity=len(self.packages))
    for package in self.packages:
      self.all_packages.insert(package)

  # Sort packages, first by delivery time, then by distance to hub
  def sort_packages(self): # O(nlogn)
    def package_sort(p: Deliverable):
      complication = 0
      deliverable_req = 1
      if p.complication is not None:
        if p.complication.delay is not None:
          if self.context.now < p.complication.delay:
            complication = 1
          elif p.complication.correction is not None:
            p.address = p.complication.correction
        if len(p.complication.deliverable_req) > 0:
          deliverable_req = 0
      deadline = p.deadline
      distance = self.routing_table.distance_to_hub(p.address)
      return complication, deadline, deliverable_req, p.city, str(p.address), p.zip, distance
      #return deadline, deliverable_req, complication, distance
      #return p.city, str(p.address), p.address.zip, complication, deadline

    self.packages.sort(key=package_sort) # O(nlogn)

  # pick a set of packages to load evenly on to the available trucks
  def load_trucksOld(self): # O(len(self.packages) * len(self.trucks) * log(len(self.packages)))
    self.sort_packages() # O(nlogn)

    # Load the trucks until full in a round-robin style to evenly split the load
    full_trucks = []
    trucks_at_hub = list(filter(lambda t: t.status == 'at hub', self.trucks)) # O(n)
    fails_to_get_package = 0
    while len(full_trucks) < len(trucks_at_hub) \
        and len(self.packages) > 0 \
        and round(fails_to_get_package/len(trucks_at_hub)-0.5) < len(self.packages): # O(n*t)
      for truck in trucks_at_hub: # O(t) t is for trucks
        if truck.status != 'at hub': continue
        if len(truck.deliverables) == truck.MAX_DELIVERABLES:
          if truck not in full_trucks: full_trucks.append(truck)
          continue

        # Now do logic to load the trucks
        # Recursive function to get a list of all required packages
        def get_required_packages(package: Deliverable, truck: Truck, known=[]): # O(n)
          required_packages = [package]
          known.append(package.id)
          if package.status != 'at hub':
            return []
          if package.complication is None: return required_packages
          if len(package.complication.deliverable_req) == 0: return required_packages
          for req in package.complication.deliverable_req:
            if req in known: continue
            req_package = self.all_packages.search(req)
            other_required_packages = get_required_packages(req_package, truck, known=known)
            if len(other_required_packages) == 0:  # If we can't find any of the required packages in the hub
              if req not in [t.id for t in truck.deliverables]:  # Check if the required package is already on the truck
                # If we got this far, it means the required packages are not on this truck
                # Abort this loading session and try loading this package on the other truck
                return []
            required_packages.extend(other_required_packages)
          return required_packages

        # Grab each package and its dependencies and load them on the truck if there are any
        if len(self.packages) > 0:
          package = self.packages[round(0 + round(fails_to_get_package/len(trucks_at_hub))-0.5)] # every failure, try for the next package
          # check if the package has some sort of complication that prevents it from getting loaded
          if package.complication is not None:
            complicated = False
            if package.complication.truck_req is not None and package.complication.truck_req != truck.id:
              complicated = True
            if package.complication.delay is not None and self.context.now < package.complication.delay:
              complicated = True
            if complicated:
              fails_to_get_package += 1
              continue
          packages_to_load = get_required_packages(package, truck)
          for p in packages_to_load:
            truck.load(p)
          # After they are loaded, remove them from the packages list
          for p in packages_to_load:
            self.packages.remove(p)
          fails_to_get_package = 0

  # TODO: fix this load trucks
  # Currently working on getting packages for the same place to go together
  def load_trucks(self):
    trucks_at_hub = [filter(lambda t: t.status == 'at hub', self.trucks)]
    for truck in trucks_at_hub:
      if len(self.packages) == 0: continue
      packages_to_load = Set()

      for package in self.packages:
        # Recursive function to get a list of all required packages
        def get_required_packages(package: Deliverable, truck: Truck, known=[]):  # O(n)
          required_packages = [package]
          known.append(package.id)
          if package.status != 'at hub':
            return []
          if package.complication is None: return required_packages
          if len(package.complication.deliverable_req) == 0: return required_packages
          for req in package.complication.deliverable_req:
            if req in known: continue
            req_package = self.all_packages.search(req)
            other_required_packages = get_required_packages(req_package, truck, known=known)
            if len(other_required_packages) == 0:  # If we can't find any of the required packages in the hub
              if req not in [t.id for t in truck.deliverables]:  # Check if the required package is already on the truck
                # If we got this far, it means the required packages are not on this truck
                # Abort this loading session and try loading this package on the other truck
                return []
            required_packages.extend(other_required_packages)
          return required_packages
        other_required_packages = get_required_packages(package, truck)
        if len(other_required_packages) == 0: continue # This package needs to be with it's required partners
        packages_to_load += other_required_packages
        packages_same_address = Set()


  # Build the routes for a truck
  def build_route(self, truck: Truck): # O(n^2logn)
    # Don't do anything if there are no packages
    if len(truck.deliverables) == 0: return

    # Get the first place closest to the hub
    ordered_packages_by_distance = list(truck.deliverables)
    ordered_packages_by_distance.sort(key=lambda x: self.routing_table.distance_to_hub(x.address))

    # Now we are guaranteed the closest package is first
    packages_by_distance_between = []

    while len(ordered_packages_by_distance) > 1: # O(n^2logn)
      # get the closest package to the current one
      record = self.routing_table.get_routing_record(ordered_packages_by_distance[0].address) # O(n)
      record = [address for address, dist in record] # O(n)
      indexes_by_distance_to_package = [(record.index(p.address), p) for p in ordered_packages_by_distance[1:]] # O(n)
      indexes_by_distance_to_package.sort(key=lambda x: x[0]) # O(nlogn)
      closest_index_package_pair = indexes_by_distance_to_package[0]
      closest_package = closest_index_package_pair[1]

      # Add the current package to the ordered list of packages
      packages_by_distance_between.append(ordered_packages_by_distance[0])

      # replace the first package in the list with the closest package
      ordered_packages_by_distance.remove(closest_package)
      ordered_packages_by_distance = ordered_packages_by_distance[1:]
      ordered_packages_by_distance.insert(0, closest_package)
    # Add the last package to be sorted to the list
    len(ordered_packages_by_distance)
    packages_by_distance_between.append(ordered_packages_by_distance[0])

    # Now the packages are ordered by distance between each other
    truck.deliverables = packages_by_distance_between

  # Function to load and plan a route for a truck
  def dispatch(self): # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
    self.load_trucks() # O(len(self.packages) * len(self.trucks) * log(len(self.packages)))
    for truck in self.trucks: # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
      if truck.status == 'at hub': self.build_route(truck) # O(n^2logn)