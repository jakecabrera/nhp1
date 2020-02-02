from nhp1.package.deliverable import Deliverable
from nhp1.package.address import Address
from nhp1.package.complication import Complication

# A class that reads in a csv for packages
class PackageReader():
  # Constructor for the PackageReader class
  def __init__(self, csv):
    self.csv = csv
    self.packages = []

  # Load the data from the csv file into the package list
  def load(self):
    with open(self.csv, 'r') as file:
      for line in file:
        line = line.replace('\n', '').split(';')
        package = Deliverable()
        package.id = int(line[0]) # get the package id
        package.address = Address(line[1] + ' (' + line[4] + ')') # Create an Address object
        package.city = line[2]
        package.zip = package.address.zip
        package.set_deadline(line[5].strip()) # Parse the deadline
        package.weight = int(line[6]) # Sets the mass of the package
        if line[7] != '': # If there are any notes, create a complication for the package
          complication = Complication()
          complication.parse(line[7].strip())
          package.complication = complication

        # add the package to the list of packages
        self.packages.append(package)
