from nhp1.datastructures.routingTable import RoutingTable
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.controller import Controller
from nhp1.package.truck import Truck
from nhp1.package.address import Address
from nhp1.datastructures.hashTable import PackageHashTable
from nhp1.package.packageGroup import PackageGroup


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

    # Build the packages list and the list of addresses we will visit
    p = PackageReader('resources/WGUPS Package File.csv')
    p.load()
    self.all_packages = PackageHashTable(initial_capacity=len(p.packages))
    for package in p.packages:  # O(len(self.all_packages))
      self.all_packages.insert(package) # O(1)

    # Build the groups of packages
    self.package_groups = []
    self.update_package_groups()  # O(len(self.all_packages)^2)

  # Create groups of packages that still need to go out based on their address
  def update_package_groups(self): # O(len(self.all_packages)^2)
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
  def sort_package_groups(self): # O(len(self.packages) * log(len(self.packages)))
    # a function used to sort the elements in the package_groups list
    def compare(group: PackageGroup): # O(1)
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

      return complication, group.deadline, deliverable_req, group.address.zip, self.routing_table.distance_to_hub(
        group.address)

    self.package_groups.sort(key=compare) # O(nlogn)

  # Currently working on getting packages for the same place to go together
  def load_trucks(self): # O(len(self.trucks)*len(self.all_packages)^3)
    trucks_at_hub = list(filter(lambda t: t.status == 'at hub', self.trucks))
    self.update_package_groups() # O(len(self.all_packages)^2)
    self.sort_package_groups() # O(len(self.all_packages) * log(len(self.all_packages)))
    for truck in trucks_at_hub: # O(len(self.trucks)*len(self.all_packages)^3) in case each package is its own group and all trucks are at hub
      truck.iteration += 1
      print('loading truck {} for batch {} at {}'.format(truck.id, truck.iteration, self.context.now))
      i = 0
      while len(truck.deliverables) < truck.MAX_DELIVERABLES and i < len(self.package_groups): # O(len(self.package_groups)^3)
        group = self.package_groups[i]

        # Recursive function to get a list of all required packages
        def get_required_packages(g: PackageGroup, truck: Truck, known=[]):  # O(len(self.package_groups)^2)
          required_packages = [g]
          known += [d.id for d in truck.deliverables]
          known += g.package_ids
          if g not in self.package_groups:
            return []
          if g.complication is None: return required_packages
          if len(g.complication.deliverable_req) == 0: return required_packages
          for req in g.complication.deliverable_req: # O(n*n) deliverable_req would be at most every other package
            if req in known: continue # check if we already have this required package

            # if not, get the group that does
            group_with_required_packages = list(filter(lambda x: req in x.package_ids, self.package_groups))[0] # O(n)
            known += group_with_required_packages.package_ids # O(1) there should only be one group with the required package
            groups_to_add = get_required_packages(group_with_required_packages, truck, known=known)

            # make sure there are no duplicates
            if group_with_required_packages in groups_to_add: groups_to_add.remove(group_with_required_packages)

            # If we can't find any of the required packages in the hub
            if len(groups_to_add) == 0:
              if req not in known: return []

            # If we found everything we needed, put all the packages together and return them
            else: groups_to_add.append(group_with_required_packages)
            required_packages.extend(groups_to_add)
          return required_packages

        required_packages = get_required_packages(group, truck) # O(len(self.package_groups)^2)
        if len(required_packages) + len(truck.deliverables) <= truck.MAX_DELIVERABLES:
          complicated = False
          for group in required_packages: # O(len(self.package_groups))
            # check if the package has some sort of complication that prevents it from getting loaded
            if group.complication is not None:
              if group.complication.truck_req is not None and group.complication.truck_req != truck.id:
                complicated = True
              if group.complication.delay is not None and self.context.now < group.complication.delay:
                complicated = True
          if complicated:
            i += 1
            continue
          else:
            i = 0

          for group in required_packages: # O(len(self.package_groups))
            print('loading {} packages on truck {}'.format(len(group), truck.id))
            result = truck.load_group(group)
            if result == True:
              self.package_groups.remove(group)
        else: i += 1

  # Build the routes for a truck
  def build_route(self, truck: Truck):  # O(n^2logn)
    # Don't do anything if there are no packages
    if len(truck.deliverables) == 0: return

    # Get the first place closest to the hub
    ordered_packages_by_distance = list(truck.deliverables)
    ordered_packages_by_distance.sort(key=lambda x: self.routing_table.distance_to_hub(x.address))

    # Now we are guaranteed the closest package is first
    packages_by_distance_between = []

    while len(ordered_packages_by_distance) > 1:  # O(n^2logn)
      # get the closest package to the current one
      record = self.routing_table.get_routing_record(ordered_packages_by_distance[0].address)  # O(n)
      record = [address for address, dist in record]  # O(n)
      indexes_by_distance_to_package = [(record.index(p.address), p) for p in ordered_packages_by_distance[1:]]  # O(n)
      indexes_by_distance_to_package.sort(key=lambda x: x[0])  # O(nlogn)
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
  def dispatch(self):  # O(len(self.trucks)*len(self.all_packages)^3) because truck.deliverables is always <= self.all_packages
    self.load_trucks()  # O(len(self.trucks)*len(self.all_packages)^3)
    for truck in self.trucks:  # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
      if truck.status == 'at hub': self.build_route(truck)  # O(n^2logn)
