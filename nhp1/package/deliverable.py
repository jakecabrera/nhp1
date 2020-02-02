from datetime import datetime


class Deliverable():
  # Constructor for the Deliverable class
  def __init__(self):  # O(1)
    self.id = None
    self.address = None
    self.zip = None
    self.deadline = None
    self.city = None
    self.weight = None
    self.status = 'at hub'
    self.complication = None

  # Set the deadline from a time given as a string
  def set_deadline(self, deadline):  # O(1)
    # If EOD, just set it to 5pm
    if deadline == 'EOD':
      self.deadline = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
    else:  # Get the time of the deadline
      hour = int(deadline.split(':')[0])
      if deadline.endswith('PM'): hour += 12
      deadline = deadline[:-2]
      minute = int(deadline.split(':')[1])
      self.deadline = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

  # Update the package in case it has any corrections to apply
  def update(self, time: datetime):  # O(1)
    if self.complication is not None and self.complication.correction is not None:
      if self.complication.delay is not None and self.complication.delay < time:
        self.address = self.complication.correction

  # Override the string operator
  def __str__(self):
    msg = 'Package: {}; status: {}; complication: {}'.format(self.id, self.status, self.complication is not None)
    if self.deadline < datetime.now().replace(hour=16, minute=59, second=59):
      msg += ' deadline: {}'.format(self.deadline)
    return msg

  # Override equal operator
  def __eq__(self, other):
    if not isinstance(other, Deliverable): return False
    return other.id == self.id

  # Override hash operator
  def __hash__(self):
    return self.id
