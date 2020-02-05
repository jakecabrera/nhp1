from nhp1.controller import Controller
from nhp1.datastructures.set import Set

class Truck():
  # Constructor for the Truck class
  def __init__(self, context: Controller,dispatch, id: int, status='at hub'):
    self.context = context
    self.id = id
    self.mileage = 0.0
    self.SPEED = 18.0
    self.status = status
    self.dest = None
    self.dist_from_dest = float('inf')
    self.gas = float('inf')
    self.deliverables = []
    self.MAX_DELIVERABLES = 16
    self.dispatch = dispatch
    self.iteration = 0
    self.zips = Set()
    self.cities = Set()

  # travels towards the destination or reaches the destination
  def travel(self): # O(trucks*packages^3)
    # Do nothing if we haven't been assigned yet
    if self.status == 'awaiting assignment': return

    # if we don't have a destination yet, set one
    if self.dest is None:
      if len(self.dispatch.package_groups) == 0: return # Don't worry if there's nothing else for us
      if len(self.deliverables) == 0: self.dispatch.dispatch()
      if len(self.deliverables) == 0: return # if we still have nothing after dispatch, there is nothing for us
      self.dest = self.deliverables[0].address
      self.dist_from_dest = self.dispatch.routing_table.distance_to_hub(self.dest)

    # Travel towards destination at avg speed
    if self.dist_from_dest > 0.0:
      dist_covered = self.SPEED * self.context.time_delta / 3600
      self.dist_from_dest -= dist_covered
      self.mileage += dist_covered

    # if at destination, deliver deliverables
    if self.dist_from_dest <= 0.0:
      if self.dest == self.dispatch.home:
        self.status = 'at hub'
        self.dispatch.dispatch() # O(trucks*packages^3)
      else:
        self.status = 'at destination'
      delivered_packages = self.deliver() # O(packages)
      for package in delivered_packages: # O(packages^2)
        self.deliverables.remove(package) # O(packages)

      # because deliveries are instant, any extra distance traveled over
      # are applied to the next destination
      overage = self.dist_from_dest * -1

      # set the new destination
      current_location = self.dest # if we still have packages to deliver, set dest to next address
      if len(self.deliverables) > 0:
        self.dest = self.deliverables[0].address
        self.dist_from_dest = self.dispatch.routing_table.distance_between(current_location, self.dest) # O(addresses)
      else:
        # If we are already home (because we delivered everything and there is nothing left to deliver)
        if current_location == self.dispatch.home:
          self.dest = None
          self.dist_from_dest = 0.0
          self.mileage -= overage
          return
        # we aren't at home, but lets go there right now
        self.dest = self.dispatch.home
        self.dist_from_dest = self.dispatch.routing_table.distance_to_hub(current_location) # O(addresses)
      self.dist_from_dest -= overage

  # load a deliverable onto the truck
  # returns whether or not the deliverable is loaded on the truck
  def load(self, deliverable): # O(1)
    if deliverable not in self.deliverables:
      if len(self.deliverables) == self.MAX_DELIVERABLES:
        return False
      deliverable.status = 'in route'
      self.zips.add(deliverable.zip)
      self.cities.add(deliverable.city)
      self.deliverables.append(deliverable)
    return True

  # load a group of packages onto the truck. Return whether or not the operation was successful
  def load_group(self, group): # O(packages) in case all packages are in one group
    all_loaded = True
    for package in group.packages:
      result = self.load(package)
      if not result: all_loaded = False
    return all_loaded

  # deliver any deliverables to the destination
  def deliver(self): # O(len(self.deliverables))
    delivered_packages = []
    for deliverable in self.deliverables:
      if deliverable.address == self.dest:
        deliverable.status = 'delivered by truck {} batch {} @ {} to {}'.format(self.id, self.iteration, self.context.now.strftime("%X"), deliverable.address)
        delivered_packages.append(deliverable)
    return delivered_packages

  # Sort packages on the truck based on distance to eachother.
  # First package is the package closest to the hub
  # next package is the package closest to the next lcoation
  # and so on
  def sort_packages(self): # O(n^2 * logn)
    # first sort by distance to the hub
    ordered_packages_by_distance = list(sorted(self.deliverables, key=lambda x: self.dispatch.routing_table.distance_to_hub(x.address)))

    # Now we are guaranteed the closest package is first
    packages_by_distance_between = []

    while len(ordered_packages_by_distance) > 1:  # O(n^2logn)
      # get the closest package to the current one
      record = self.dispatch.routing_table.get_routing_record(ordered_packages_by_distance[0].address)  # O(n)
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
    if len(ordered_packages_by_distance) >= 1:
      packages_by_distance_between.append(ordered_packages_by_distance[0])

    # Now the packages are ordered by distance between each other
    self.deliverables = packages_by_distance_between

  # Override the hash function for use in the hash table
  def __hash__(self):
    return self.id

  # Override equality operator for use with comparing trucks
  def __eq__(self, other):
    if not isinstance(other, Truck): return False
    return self.id == other.id
