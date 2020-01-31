import nhp1.datastructures.graph
from datetime import datetime
from nhp1.data.distanceReader import DistanceReader

print('Hello World')
d = DistanceReader('resources/WGUPS Distance Table.csv')
d.load()
for address in d.addresses:
  print(address)
for row in d.distance_matrix:
  print(row)
