from nhp1.datastructures.routingTable import RoutingTable
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.controller import Controller
from nhp1.package.deliverable import Deliverable
from nhp1.package.truck import Truck
from nhp1.package.address import Address
from nhp1.datastructures.hashTable import PackageHashTable
from nhp1.datastructures.set import Set
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
    self.addresses = []
    self.all_packages = PackageHashTable(initial_capacity=len(p.packages))
    for package in p.packages:
      self.all_packages.insert(package)
      if package.address not in self.addresses:
        self.addresses.append(package.address)

    # Build the groups of packages
    self.package_groups = []
    self.update_package_groups()

  # Create groups of packages that still need to go out based on their address
  def update_package_groups(self):
    # List of all packages at the hub
    packages = self.all_packages.lookup_status('at hub')

    # make sure all packages are up to date
    for package in packages:
      package.update(self.context.now)

    while len(packages) > 0:
      # get all packages going to the same address as the first one in the list
      group = PackageGroup(packages[0].address)

      # check if there is a correction to be made
      def has_no_correction(elem):
        complication = elem.complication
        return complication is None or complication.correction is None

      # if the package has a correction to be made, make own group
      if not has_no_correction(packages[0]):
        group.append(packages[0])
        packages.remove(packages[0])

      else:
        packages_going_to_same_address = self.all_packages.lookup_address(group.address)
        packages_going_to_same_address = list(filter(has_no_correction, packages_going_to_same_address))

        # filter for only packages at the hub
        def is_currently_at_the_hub(p):
          return p.status == 'at hub'

        packages_going_to_same_address = list(filter(is_currently_at_the_hub, packages_going_to_same_address))

        # add all those packages to the group
        for package in packages_going_to_same_address:
          group.append(package)
          packages.remove(package)

      self.package_groups.append(group)

  # Sort package groups first by if they have any complications, then by their deadline, then by if they have any
  # dependent packages to be delivered with, then by distance to the hub
  def sort_package_groups(self):
    def compare(group: PackageGroup):
      complication = 0
      deliverable_req = 1
      if group.complication is not None:
        if group.complication.delay is not None:
          if self.context.now < group.complication.delay:
            complication = 1
          elif group.complication.correction is not None:
            group.address = group.complication.correction
        if len(group.complication.deliverable_req) > 0:
          deliverable_req = 0

      return complication, group.deadline, deliverable_req, group.address.zip, self.routing_table.distance_to_hub(
        group.address)

    self.package_groups.sort(key=compare)

  # Sort packages, first by delivery time, then by distance to hub
  def sort_packages(self):  # O(nlogn)
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
      # return deadline, deliverable_req, complication, distance
      # return p.city, str(p.address), p.address.zip, complication, deadline

    self.packages.sort(key=package_sort)  # O(nlogn)

  # Currently working on getting packages for the same place to go together
  def load_trucks(self):
    trucks_at_hub = list(filter(lambda t: t.status == 'at hub', self.trucks))
    self.update_package_groups()
    self.sort_package_groups()
    for truck in trucks_at_hub:
      truck.iteration += 1
      print('loading truck {} for batch {} at {}'.format(truck.id, truck.iteration, self.context.now))
      i = 0
      while len(truck.deliverables) < truck.MAX_DELIVERABLES and i < len(self.package_groups):
        group = self.package_groups[i]

        # Recursive function to get a list of all required packages
        def get_required_packages(g: PackageGroup, truck: Truck, known=[]):  # O(n)
          required_packages = [g]
          known += [d.id for d in truck.deliverables]
          known += g.package_ids
          if g not in self.package_groups:
            return []
          if g.complication is None: return required_packages
          if len(g.complication.deliverable_req) == 0: return required_packages
          for req in g.complication.deliverable_req:
            if req in known: continue
            groups_with_required_packages = list(filter(lambda x: req in x.package_ids, self.package_groups))
            for already_retrieved_group in required_packages:
              if already_retrieved_group in groups_with_required_packages:
                groups_with_required_packages.remove(already_retrieved_group)
            groups_to_add = []
            for other_group in groups_with_required_packages:
              known += other_group.package_ids
              groups_to_add += get_required_packages(other_group, truck, known=known)
            for already_retrieved_group in groups_with_required_packages:
              if already_retrieved_group in groups_to_add: groups_to_add.remove(already_retrieved_group)
            if len(groups_to_add) == 0:  # If we can't find any of the required packages in the hub
              if req not in known: return []
            else: groups_with_required_packages += groups_to_add
            required_packages.extend(groups_with_required_packages)
          return required_packages

        required_packages = get_required_packages(group, truck)
        if len(required_packages) + len(truck.deliverables) <= truck.MAX_DELIVERABLES:
          complicated = False
          for group in required_packages:
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

          for group in required_packages:
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
  def dispatch(self):  # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
    self.load_trucks()  # O(len(self.packages) * len(self.trucks) * log(len(self.packages)))
    for truck in self.trucks:  # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
      if truck.status == 'at hub': self.build_route(truck)  # O(n^2logn)
