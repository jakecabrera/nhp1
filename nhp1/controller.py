# First name: Jake
# Last name: Cabrera
# Student ID: 000993409

from datetime import datetime, timedelta

# class to be used to control the setting (i.e. time of day)
class Controller():
  # Constructor for the Controller class
  def __init__(self):
    self.now = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    self.time_delta = 60.0 # one minute
    self.dispatch = None
    self.snapshot_times = []

  # Advance time by 1 minute
  def advance(self): # O((trucks^2)*(packages^3))
    self.now = self.now + timedelta(seconds=self.time_delta)
    time_in_seconds = (self.now.replace(microsecond=0) - self.now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

    # Move the trucks forward by 1 minutes worth of distance and do everything a truck would do in that minute (e.g.
    # load packages, deliver, etc.)
    for truck in self.dispatch.trucks: # O((trucks^2)*(packages^3))
      # truck 2 is awaiting assignment and will leave at 9:05am
      if truck.status == 'awaiting assignment' and time_in_seconds >= (60*60*9) + (60*5):
        truck.status = 'at hub'
      truck.travel() # O(trucks*packages^3)

    # Print out the state of all of the packages at specified times
    if time_in_seconds in self.snapshot_times:
      print('\n\n\n\n\n\n\n')
      print('Snapshot at {}'.format(self.now.strftime("%X")))
      for package in self.dispatch.all_packages: # O(packages)
        print(package)

  # make the controller print the statuses of all the packages at the given time
  # should be between 8:00am to 5:00pm because that is how long the day is simulated for
  # otherwise you probably won't see your statuses printed
  def show_package_statuses_at_time(self, time: datetime):
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_today_in_seconds = (time.replace(microsecond=0) - midnight).total_seconds()
    self.snapshot_times.append(time_today_in_seconds)