import re

class Address():
  # Patterns for parsing a string for address
  address_pattern = re.compile(r"^.*(?=\()")
  zip_pattern = re.compile(r"(?<=\()\d*(?=\))")

  # Constructor for the Address class
  def __init__(self, address_raw):
    self.address = None
    self.zip = None
    self.parse(address_raw)

  # parse the raw address for the necessary fields
  def parse(self, data):
    data = data.strip() # get rid of those extra white spaces
    # If this is the Hub, set it uniquely
    if data == 'HUB':
      self.address = 'HUB'
      self.zip = 84107
      return

    # Extract the address and zip and set the appropriate values
    for match in Address.address_pattern.findall(data):
      # Also fix inconsistencies with address naming
      self.address = match.strip().replace('South', 'S').replace('East', 'E').replace('West', 'W').replace('North', 'N')
    for match in Address.zip_pattern.findall(data):
      self.zip = int(match)

  # Override of the hash function for use in a hash table
  def __hash__(self):
    return hash(self.address) + zip

  # Override of the equality operator for use in comparing two addresses
  def __eq__(self, other):
    if not isinstance(other, Address): return False
    return self.address == other.address and self.zip == other.zip

  # Override the string method
  def __str__(self):
    return self.address + ' (' + str(self.zip) + ')'
