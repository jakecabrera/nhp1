from datetime import datetime

class Deliverable():
  # Constructor for the Deliverable class
  def __init__(self):
    self.id = None
    self.address = None
    self.deadline = None
    self.mass = None
    self.status = 'at hub'
    self.complication = None

  def set_deadline(self, deadline):
    # If EOD, just set it to 5pm
    if deadline == 'EOD':
      self.deadline = datetime.now().replace(hour=17, minute=0, second=0)

    # Get the time of the deadline
    hour = int(deadline.split(':')[0])
    if deadline.endswith('PM'): hour += 12
    deadline = deadline[:-2]
    minute = deadline.split(':')[1]
    self.deadline = datetime.now().replace(hour=hour,minute=minute,second=0)
