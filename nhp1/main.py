# First name: Jake
# Last name: Cabrera
# Student ID: 000993409

from datetime import datetime
from nhp1.package.dispatch import Dispatch
from nhp1.controller import Controller
from nhp1.package.truck import Truck


controller = Controller()
controller.dispatch = Dispatch(controller)
d = controller.dispatch
d.trucks = [Truck(controller, d, 1), Truck(controller, d, 2)]
d.dispatch() # O(trucks * packages^3)
end_time = datetime.now().replace(hour=17,minute=0,second=0, microsecond=0) # 5pm

# show package statuses at specified times
time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

controller.show_package_statuses_at_time(time.replace(hour=9)) # 9:00am
controller.show_package_statuses_at_time(time.replace(hour=10)) # 10:00am
controller.show_package_statuses_at_time(time.replace(hour=13)) # 1:00pm

# simulate the world
while controller.now < end_time:
  controller.advance()

# Get total miles
total_miles = sum(x.mileage for x in d.trucks)
print('Total mileage: {}'.format(total_miles))
