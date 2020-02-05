from nhp1.datastructures.routingTable import RoutingTable
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.controller import Controller
from nhp1.package.truck import Truck
from nhp1.package.address import Address
from nhp1.datastructures.hashTable import PackageHashTable
from nhp1.package.packageGroup import PackageGroup
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

    # Build the packages list and the list of addresses we will visit
    p = PackageReader('resources/WGUPS Package File.csv')
    p.load()
    self.addresses = []
    self.all_packages = PackageHashTable(initial_capacity=len(p.packages))
    for package in p.packages:  # O(len(self.all_packages))
      self.all_packages.insert(package) # O(1)
      if package.address not in self.addresses:
        self.addresses.append(package.address)

    # Build the routing matrix
    self.routing_table.build_routing_matrix(self.addresses)

    # Build the groups of packages
    self.package_groups = []
    self.update_package_groups()  # O(len(self.all_packages)^2)

  # Create groups of packages that still need to go out based on their address
  def update_package_groups(self): # O(packages^2)
    self.package_groups = [] # clear the list

    # List of all packages at the hub
    packages = self.all_packages.lookup_status('at hub') # O(len(self.all_packages))

    # make sure all packages are up to date
    for package in packages: # O(len(self.all_packages))
      package.update(self.context.now)

    while len(packages) > 0: # O(len(self.all_packages)^2) in case every package is at the hub and all packages have unique addresses
      # get all packages going to the same address as the first one in the list
      group = PackageGroup(packages[0].address)

      # check if there is a correction to be made
      def has_no_correction(elem): # O(1)
        complication = elem.complication
        return complication is None or complication.correction is None

      # if the package has a correction to be made, make own group
      if not has_no_correction(packages[0]):
        group.append(packages[0])
        packages.remove(packages[0])

      else:
        packages_going_to_same_address = self.all_packages.lookup_address(group.address) # O(len(self.all_packages))
        packages_going_to_same_address = list(filter(has_no_correction, packages_going_to_same_address)) # O(len(self.all_packages))

        # filter for only packages at the hub
        def is_currently_at_the_hub(p): # O(1)
          return p.status == 'at hub'

        packages_going_to_same_address = list(filter(is_currently_at_the_hub, packages_going_to_same_address)) # O(len(self.all_packages))

        # add all those packages to the group
        for package in packages_going_to_same_address: # O(len(self.all_packages)) in case all packages are for one address
          group.append(package)
          packages.remove(package)

      self.package_groups.append(group)

  # Sort package groups first by if they have any complications, then by their deadline, then by if they have any
  # dependent packages to be delivered with, then by distance to the hub
  def sort_package_groups(self): # O(packages * log(packages) * addresses)
    # a function used to sort the elements in the package_groups list
    def compare(group: PackageGroup): # O(addresses)
      complication = 0
      deliverable_req = 1

      # check if the packages have any complications
      if group.complication is not None:

        # check if the packages are delayed at all
        if group.complication.delay is not None:
          if self.context.now < group.complication.delay:
            complication = 1

            # For the case of the address in need of correction, correct it at the appropriate time
          elif group.complication.correction is not None:
            group.address = group.complication.correction

        # check if any of the packages need to be with any other packages
        if len(group.complication.deliverable_req) > 0:
          deliverable_req = 0

      return complication, deliverable_req, group.deadline, group.address.zip, self.routing_table.distance_to_hub(
        group.address)

    self.package_groups.sort(key=compare) # O(nlogn*addresses)

  # Currently working on getting packages for the same place to go together
  def load_trucks(self): # O(trucks * packages^3)
    trucks_at_hub = list(filter(lambda t: t.status == 'at hub', self.trucks))
    self.update_package_groups() # O(len(self.all_packages)^2)
    self.sort_package_groups() # O(len(self.all_packages) * log(len(self.all_packages)))
    for truck in trucks_at_hub: # O(len(self.trucks)*len(self.all_packages)^3) in case each package is its own group and all trucks are at hub
      truck.iteration += 1
      i = 0
      while len(truck.deliverables) < truck.MAX_DELIVERABLES and i < len(self.package_groups): # O(len(self.package_groups)^3)
        group = self.package_groups[i]

        required_packages = self.get_required_packages(group) # O(packages^2)
        if len(required_packages) + len(truck.deliverables) <= truck.MAX_DELIVERABLES:
          complicated = False
          for group in required_packages: # O(packages)
            if group.is_complicated(truck, self.context): complicated = True
          if complicated:
            i += 1
            continue
          else:
            i = 0

          for group in required_packages: # O(packages)
            result = truck.load_group(group)
            if result == True:
              self.package_groups.remove(group)
        else: i += 1

  # Function to load and plan a route for a truck
  def dispatch(self):  # O(trucks*packages^3) because truck.deliverables is always <= self.all_packages
    self.load_trucks()  # O(len(self.trucks)*len(self.all_packages)^3)
    for truck in self.trucks:  # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
      if truck.status == 'at hub':
        truck.sort_packages() # O(n^2logn)

  # Retrieve all package groups that have the required packages
  # worst case is each package requires every other package and every package
  # was in its own group which would make this complexity O(packages^2)
  def get_required_packages(self, group: PackageGroup, known=Set()):
    groups_with_required_packages = [group]
    known.add_all(group.package_ids)

    # If this group has a delivery requirement, get all the required package groups
    if group.complication is not None and len(group.complication.deliverable_req) > 0:

      # Get the required packages for each individual requirement
      for required_package_id in group.complication.deliverable_req:

        # if we already have it, don't worry about it
        if required_package_id in known: continue

        # find the group that contains the package you are looking for
        for potential_group in self.package_groups:
          if required_package_id in potential_group:

            # Also get that package groups required packages
            groups_with_required_packages += self.get_required_packages(potential_group, known=known)

      # add all the new package ids we got to the known list and return what we found
      for group in groups_with_required_packages:
        known.add_all(group.package_ids)
      return groups_with_required_packages

    # This package has no delivery requirements, return itself
    else:
      return groups_with_required_packages

  # Interface to see status of all packages
  def get_package_statuses(self): # O(packages)
    for package in self.all_packages: # O(packages)
      print(package)
