'''
Created on Mar 30, 2011

@author: Matthew Boggan
'''

import Puzzlebox.Brainstorms.iRobot.pyrobot as pyrobot
import time
import sys

import Configuration as configuration

MOVE_DELAY = configuration.IROBOT_MOVE_DELAY
TURN_DELAY = configuration.IROBOT_TURN_DELAY
SERIAL_TIMEOUT = configuration.IROBOT_SERIAL_TIMEOUT

BLUETOOTH_DEVICE = configuration.IROBOT_BLUETOOTH_DEVICE
DEFAULT_RC_COMMAND = configuration.IROBOT_DEFAULT_RC_COMMAND
DEBUG = 1
VARIABLE_CONTROL_DURATION = configuration.BRAINSTORMS_VARIABLE_CONTROL_DURATION

IROBOT_VELOCITY_MAX = configuration.IROBOT_VELOCITY_MAX
IROBOT_VELOCITY_SLOW = configuration.IROBOT_VELOCITY_SLOW
IROBOT_VELOCITY_FAST = configuration.IROBOT_VELOCITY_FAST
IROBOT_TURN_SPEED = configuration.IROBOT_TURN_SPEED

class irobot_control:
  
  def __init__(self, device_address=BLUETOOTH_DEVICE, command=DEFAULT_RC_COMMAND, DEBUG=DEBUG):
    self.DEBUG = DEBUG
    print "Initializing iRobot Control"
    #self.robot = pyrobot.Create('COM40')
    self.robot = pyrobot.Create(device_address)
    self.command = command
    
    
    self.device_address = device_address
    try:
      self.connection = self.robot.sci
      self.connection.Open()
    except Exception, e:
      if self.DEBUG:
        print "<-- [iRobot_RC] Connection failed to iRobot device [%s]" % self.device_address
        print "ERROR [iRobot_RC]:",
        print e
    self.robot.Control()
    
    
  def drive_forward(self,power,safe=True):
    """Drive forward."""
    self.robot.DriveStraight(IROBOT_VELOCITY_SLOW*(0.1*power))
    if not VARIABLE_CONTROL_DURATION:
      print "Not VARIABLE"
      time.sleep(MOVE_DELAY)
      self.stop_motors()


  def drive_reverse(self,power):
    """Drive in reverse."""
    self.robot.DriveStraight(-IROBOT_VELOCITY_SLOW*(0.1*power))
    if not VARIABLE_CONTROL_DURATION:
      time.sleep(MOVE_DELAY)
      self.stop_motors()

  def turn_right(self):
    """Turn in place to the right."""
    self.robot.TurnInPlace(IROBOT_TURN_SPEED, 'cw')
    time.sleep(TURN_DELAY)
    self.stop_motors()

  def turn_left(self):
    """Turn in place to the left."""
    self.robot.TurnInPlace(IROBOT_TURN_SPEED, 'ccw')
    time.sleep(TURN_DELAY)
    self.stop_motors()
    
  def stop_motors(self):
    """Stop the robot"""
    self.robot.Stop()
    
  def reset(self):
    """Stop the robot"""
    self.robot.SoftReset()
        
  def test_drive(self):
    print "Welcome to the iRobot Controller Interface"
  
    while True:
      print "What would you like the robot to do? Go [f]orward, turn [r]ight, turn [l]eft, re[v]erse or [q]? (f, r, l, v, q)"
      command = raw_input()
      if command == 'f':
        #print "forward"
        self.drive_forward()
      elif command == 'r':
        #print "right"
        self.turn_right()
      elif command == 'l':
        #print "left"
        self.turn_left()
      elif command == 'v':
        #print "reverse"
        self.drive_reverse()
      elif command == 'q':
        break
      elif command == '#':
        self.reset()
      else:
        print "Invalid command."
    
    print "Thank you for using the iRobot Controller Interface"
  
  def run(self, command, power=80):
    if (command == 'drive_forward'):
      self.drive_forward(power)
    elif(command == 'drive_reverse'):
      self.drive_reverse(power)
    elif(command == 'turn_left'):
      self.turn_left()
    elif(command == 'turn_right'):
      self.turn_right()
    elif(command == 'stop_motors'):
      self.stop_motors()
    elif(command == 'test_drive'):
      self.test_drive()
    
  def stop(self):
    self.robot.sci.Close()

  def get_status(self, connection=None):
    return('Status N/A')
        
        
if __name__ == '__main__':
    device_address = BLUETOOTH_DEVICE
    command = DEFAULT_RC_COMMAND
    
    for each in sys.argv:
        if each.startswith("--device="):
            device_address = each[len("--device="): ]
        elif each.startswith("--command="):
            command = each[len("--command="): ]
            
    rc = irobot_control(device_address, command)
    
    rc.run(rc.command)
    rc.stop()
