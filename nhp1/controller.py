from datetime import datetime, timedelta

# class to be used to control the setting (i.e. time of day)
class Controller():
  # Constructor for the Controller class
  def __init__(self):
    self.now = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    self.time_delta = 60.0 # one minute
    self.dispatch = None
    self.snapshot_times = [
      60*60*9, # 9:00am
      60*60*10, # 10:00am
      60*60*13 # 1:00pm
    ]

  # Advance time by 1 minute
  def advance(self):
    self.now = self.now + timedelta(seconds=self.time_delta)
    time_in_seconds = (self.now.replace(microsecond=0) - self.now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

    # Move the trucks forward by 1 minutes worth of distance and do everything a truck would do in that minute (e.g. load packages, deliver, etc.)
    for truck in self.dispatch.trucks:
      if truck.status == 'awaiting assignment' and time_in_seconds >= (60*60*9) + (60*5): # truck 2 is awaiting assignment and will leave at 9:05am
        truck.status = 'at hub'
      truck.travel()

    # Print out the state of all of the packages at specified times
    if time_in_seconds in self.snapshot_times:
      print('Snapshot at {} seconds'.format(time_in_seconds))
      for package in self.dispatch.all_packages: # O(len(self.dispatch.all_packages))
        print(package)

