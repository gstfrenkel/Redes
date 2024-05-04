class Logger:
  def __init__(self, show_msgs):
    self.show_msgs = show_msgs

  def print_msg(self, msg):
    if self.show_msgs:
      print(msg)