from datetime import datetime
from nhp1.package.dispatch import Dispatch
from nhp1.controller import Controller
from nhp1.package.truck import Truck

print('Hello World')
controller = Controller()
controller.dispatch = Dispatch(controller)
d = controller.dispatch
d.trucks = [Truck(controller, d, 1), Truck(controller, d, 2, status='awaiting assignment')]
d.dispatch() # O(len(self.trucks)* len(truck.deliverables)^2 * log(len(truck.deliverables))))
end_time = datetime.now().replace(hour=17,minute=0,second=0, microsecond=0)
while controller.now < end_time:
  controller.advance()
total_miles = sum(x.mileage for x in d.trucks)
print(total_miles)

