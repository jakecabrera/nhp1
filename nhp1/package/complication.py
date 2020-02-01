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
  def parse(self, data):
    # For getting a truck requirement
    if data.startswith('Can only be on truck '):
      self.truck_req = int(data[len('Can only be on truck '):])
    # deliverable requirements
    elif data.startswith('Must be delivered with '):
      deliverables = data[len('Must be delivered with '):].split(',')
      deliverables = list(map(int, deliverables))
      for id in deliverables:
        self.deliverable_req.add(id)
    # For delays
    elif data.startswith('Delayed on flight'):
      delay = data[len('Delayed on flight---will not arrive to depot until '):]
      hour = int(delay.split(':')[0])
      if delay.upper().endswith('PM'): hour += 12
      delay = delay[:-2]
      minute = int(delay.split(':')[1])
      self.delay = datetime.now().replace(hour=hour, minute=minute, second=0)
    # for the wrong address listed case
    elif data.startswith('Wrong address listed'):
      self.delay = datetime.now().replace(hour=10, minute=20, second=0)  # 10:20am
      self.correction = Address('410 S State St (84111)')
