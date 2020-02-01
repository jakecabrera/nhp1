from nhp1.datastructures.set import Set
from nhp1.controller import Controller


class Truck():
  # Constructor for the Truck class
  def __init__(self, context: Controller, id: int):
    self.context = context
    self.id = id
    self.mileage = 0.0
    self.SPEED = 18.0
    self.status = 'at hub'
    self.dest = None
    self.route = None
    self.dist_from_dest = float('inf')
    self.gas = float('inf')
    self.deliverables = []
    self.MAX_DELIVERABLES = 16

  # travels towards the destination or reaches the destination
  def travel(self):
    # Travel towards destination at avg speed
    self.dist_from_dest -= self.SPEED * self.context.time_delta / 3600

    # if at destination, deliver deliverables
    if self.dist_from_dest <= 0.0:
      self.status = 'at destination'
      self.deliver()

      # because deliveries are instant, any extra distance traveled over
      # are applied to the next destination
      overage = self.dist_from_dest * -1

      # set the new destination
      self.dest = self.route.pop()
      if self.dest is None:
        pass  # TODO: assign a new route

      # TODO: assign new destination
      self.dist_from_dest -= overage

  # load a deliverable onto the truck
  # returns whether or not the deliverable is loaded on the truck
  def load(self, deliverable):
    if deliverable not in self.deliverables:
      if len(self.deliverables) == self.MAX_DELIVERABLES:
        return False
      deliverable.status = 'in route'
      self.deliverables.add(deliverable)
    return True

  # deliver any deliverables to the destination
  def deliver(self):
    delivered_packages = Set()
    for deliverable in self.deliverables:
      if deliverable.address == self.dest:
        deliverable.status = 'delivered @ %s' % self.context.now.strftime("%X")
        delivered_packages.add(deliverable)

  # Override the hash function for use in the hash table
  def __hash__(self):
    return self.id

  # Override equality operator for use with comparing trucks
  def __eq__(self, other):
    if not isinstance(other, Truck): return False
    return self.id == other.id
