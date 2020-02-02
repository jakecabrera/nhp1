from datetime import datetime
from nhp1.package.dispatch import Dispatch
from nhp1.controller import Controller
from nhp1.package.truck import Truck

print('Hello World')
controller = Controller()
controller.dispatch = Dispatch(controller)
d = controller.dispatch
# d.trucks = [Truck(controller, d, 1), Truck(controller, d, 2, status='awaiting assignment')]
d.trucks = [Truck(controller, d, 1), Truck(controller, d, 2)]
d.dispatch() # O(trucks * packages^3)
end_time = datetime.now().replace(hour=17,minute=0,second=0, microsecond=0)
while controller.now < end_time:
  controller.advance()
total_miles = sum(x.mileage for x in d.trucks)
print(total_miles)

# TODO: how did 19 get on truck 2?
