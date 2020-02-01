import nhp1.datastructures.graph
from datetime import datetime
from nhp1.data.distanceReader import DistanceReader
from nhp1.data.packageReader import PackageReader
from nhp1.datastructures.routingTable import RoutingTable
from nhp1.package.address import Address
from nhp1.package.dispatch import Dispatch
from nhp1.controller import Controller
from nhp1.package.truck import Truck

print('Hello World')
controller = Controller()
d = Dispatch(controller)
d.sort_packages()
d.trucks = [Truck(controller, 1), Truck(controller, 2)]
d.load_trucks()
