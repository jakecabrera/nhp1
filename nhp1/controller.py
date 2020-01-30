from datetime import datetime, timedelta


# class to be used to control the setting (i.e. time of day)
class Controller():
  # Constructor for the Controller class
  def __init__(self):
    self.now = datetime.now().replace(hour=8, minute=0, second=0)
    self.time_delta = 0.0

  # Advance time by 1 minute
  def advance(self):
    self.now = self.now + timedelta(seconds=60)
