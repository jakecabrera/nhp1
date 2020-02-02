from datetime import datetime


# Class to handle the grouping of packages
class PackageGroup():
  # Constructor for the PackageGroup class
  def __init__(self, address):  # O(1)
    self.address = address
    self.packages = []
    self.package_ids = []
    self._complications = []
    self.deadline = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
    self.combined_complication = None  # The merged complication of all packages in this group

  # To return the complications list
  @property
  def complications(self):  # O(1)
    return self._complications

  # For when we set the complications list, we also update the combined complications
  @complications.setter
  def complications(self, value):  # O(packages^2) if every package required to be with every other package
    self._complications = value
    if len(self._complications) >= 1:
      self.combined_complication = self._complications[0]
      if len(self._complications) > 1:
        for complication in self._complications:  # O(n^2)
          self.combined_complication.merge(complication)  # O(n)
    else:
      self.combined_complication = None

  # Just an alias for self.combined_complication
  @property
  def complication(self):  # O(1)
    return self.combined_complication

  # Override len operator
  def __len__(self):  # O(1)
    return len(self.packages)

  # Add a package to this group
  def append(self, package):  # O(1)
    self.packages.append(package)
    if package.complication is not None: self.complications = list(self._complications + [package.complication])
    self.package_ids.append(package.id)
    if package.deadline < self.deadline: self.deadline = package.deadline

  # Remove a package from this group
  def remove(self, package):  # O(packages)
    self.packages.remove(package)
    self._complications.remove(package.complication)
    self.complications = list(self._complications)  # re-update the combined_complication
    self.package_ids.remove(package.id)
    self.deadline = min(p.deadline for p in self.packages)

  # Clear all packages from this group
  def clear(self):  # O(1)
    self.packages = []
    self.package_ids = []
    self.complications = []
    self.combined_complication = None
