class Address():
  # Constructor for the Address class
  def __init__(self):
    self.address = None
    self.state = None
    self.zip = None

  # Override of the hash function for use in a hash table
  def __hash__(self):
    return hash(self.zip) + hash(self.address) + hash(self.state)

  # Override of the equality operator for use in comparing two addresses
  def __eq__(self, other):
    if not isinstance(other, Address): return False
    if other.zip is None or other.zip != self.zip: return False
    if other.address is None or other.address != self.address: return False
    return True
