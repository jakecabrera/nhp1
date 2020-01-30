from nhp1.datastructures.set import Set

# Represents the special notes of a Deliverable
class Complication():
  # Constructor for the Complication class
  def __init__(self):
    self.complication_raw = None # string of special note
    self.delay = None # datetime
    self.truck_req = None # truck id
    self.deliverable_req = Set() # list of package ids that are required to be with it
