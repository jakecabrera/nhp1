from nhp1.package.deliverable import Deliverable


# HashTable class
class HashTable:
  # Constructor with optional initial capacity parameter.
  # Assigns all buckets with None.
  def __init__(self, initial_capacity=10):
    # initialize the hash table with empty bucket entries
    self.table = [None for i in range(initial_capacity)]

  # Inserts a new item into the hash table.
  def insert(self, item):
    # get the bucket where this item will go.
    bucket = hash(item) % len(self.table)

    # insert the item and replace whatever was there before
    self.table[bucket] = item

  # Searches for an item with matching key in the hash table.
  # Returns the item if found, or None if not found.
  def search(self, key):
    # get the bucket where this key would be.
    bucket = hash(key) % len(self.table)

    # return what is in that bucket
    return self.table[bucket]

  # Removes an item with matching key from the hash table.
  def remove(self, key):
    # get the bucket list where this item will be removed from.
    bucket = hash(key) % len(self.table)

    # set that bucket to None
    self.table[bucket] = None

  # Make the object iterable
  def __iter__(self):
    self.n = 0
    return self

  def __next__(self):
    if self.n < len(self.table):
      self.n += 1
      return self.table[self.n-1]
    else:
      raise StopIteration


# Hash Table specifically for Packages
class PackageHashTable(HashTable):
  # Get an iterable of all the packages currently in the hash table
  def items(self):
    def is_package(elem):
      return isinstance(elem, Deliverable)

    return list(filter(is_package, self.table))

  # below are the lookup functions for each attribute required
  # This is the main lookup function
  def lookup_attr(self, value, attr):
    matches = []
    for package in self.items():
      package_attr = getattr(package, attr, None)
      if package_attr is None: continue
      if attr == 'status':  # This is because delivered statuses also have the time it was delivered
        if package_attr.startswith(value): matches.append(package)
      elif package_attr == value:
        matches.append(package)
    return matches

  # Lookup a package by its id
  def lookup_id(self, id):
    return self.lookup_attr(id, 'id')

  # Lookup a package by its address
  def lookup_address(self, address):
    return self.lookup_attr(address, 'address')

  # Lookup a package by its deadline
  def lookup_deadline(self, deadline):
    return self.lookup_attr(deadline, 'deadline')

  # Lookup a package by its city
  def lookup_city(self, city):
    return self.lookup_attr(city, 'city')

  # Lookup a package by its zip code
  def lookup_zip(self, zip):
    return self.lookup_attr(zip, 'zip')

  # Lookup a package by its weight
  def lookup_weight(self, weight):
    return self.lookup_attr(weight, 'weight')

  # Lookup a package by its status
  def lookup_status(self, status):
    return self.lookup_attr(status, 'status')
