from nhp1.datastructures.set import Set
from nhp1.package.address import Address
from datetime import datetime


# Represents the special notes of a Deliverable
class Complication():
  # Constructor for the Complication class
  def __init__(self):
    self.complication_raw = None  # string of special note
    self.delay = None  # datetime
    self.truck_req = None  # truck id
    self.deliverable_req = Set()  # list of package ids that are required to be with it
    self.correction = None

  # Parse the correct complication from a raw string
  def parse(self, data): # O(packages)
    # For getting a truck requirement
    if data.startswith('Can only be on truck '):
      self.truck_req = int(data[len('Can only be on truck '):])

    # deliverable requirements
    elif data.startswith('Must be delivered with '):
      deliverables = data[len('Must be delivered with '):].split(',')
      deliverables = list(map(int, deliverables))
      for id in deliverables: # O(packages) in case every package id is listed as required
        self.deliverable_req.add(id)

    # For delays
    elif data.startswith('Delayed on flight'):
      delay = data[len('Delayed on flight---will not arrive to depot until '):]
      hour = int(delay.split(':')[0])
      if delay.upper().endswith('PM'): hour += 12
      delay = delay[:-2]
      minute = int(delay.split(':')[1])
      self.delay = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

    # for the wrong address listed case
    elif data.startswith('Wrong address listed'):
      self.delay = datetime.now().replace(hour=10, minute=20, second=0, microsecond=0)  # 10:20am
      self.correction = Address('410 S State St (84111)')

  # Merge two complications
  def merge(self, other): # O(n)
    # Use the latest delay
    self.delay = self.delay if other.delay < self.delay else other.delay

    # Use the truck req of whichever has one, or if they are the same. Throw exception if different
    if self.truck_req is None or other.truck_req == self.truck_req: self.truck_req = other.truck_req
    else: raise ValueError('Mismatched truck requirements')

    # Merge the deliverable requirements
    self.deliverable_req = self.deliverable_req.union(other.deliverable_req)

    # Use the correction of whichever has one, or if they are the same. Throw exception if different
    if self.correction is None or self.correction == other.correction: self.correction = other.correction
    else: raise ValueError('Mismatched corrections')
