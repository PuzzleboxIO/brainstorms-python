#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - NXT Control
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """
Last Update: 2012.04.03
"""

import sys, time
import serial

import jaraco.nxt
import jaraco.nxt.messages

import Configuration as configuration

#####################################################################
# Globals
#####################################################################

DEBUG = 1

VARIABLE_CONTROL_DURATION = configuration.BRAINSTORMS_VARIABLE_CONTROL_DURATION

BLUETOOTH_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

DEFAULT_NXT_POWER_LEVEL = configuration.DEFAULT_NXT_POWER_LEVEL

MOTORS_MOUNTED_BACKWARDS = configuration.NXT_MOTORS_MOUNTED_BACKWARDS
MOTOR_PORT_RIGHT = configuration.NXT_MOTOR_PORT_RIGHT
MOTOR_PORT_LEFT = configuration.NXT_MOTOR_PORT_LEFT
DEFAULT_RC_COMMAND = configuration.NXT_DEFAULT_RC_COMMAND

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_nxt_control:
	
	def __init__(self, \
	             device_address=BLUETOOTH_DEVICE, \
	             command=DEFAULT_RC_COMMAND, \
	             motors_mounted_backwards=MOTORS_MOUNTED_BACKWARDS,\
	             motor_port_right=MOTOR_PORT_RIGHT,\
	             motor_port_left=MOTOR_PORT_LEFT,\
	             DEBUG=DEBUG):
		
		self.DEBUG = DEBUG
		
		self.device_address = device_address
		self.command = command
		
		self.motors_mounted_backwards = motors_mounted_backwards
		self.motor_port_right = motor_port_right
		self.motor_port_left = motor_port_left
		
		self.connection = None
		
		try:
			self.connection = self.connect_to_nxt(self.device_address)
		except Exception, e:
			if self.DEBUG:
				print "<-- [NXT_RC] Connection failed to NXT device [%s]" % self.device_address
				print "ERROR [NXT_RC]:",
				print e
	
	
	##################################################################
	
	def connect_to_nxt(self, device_address):
		
		connection = jaraco.nxt.Connection(self.device_address)
		
		if self.DEBUG:
			battery_voltage = self.get_battery_voltage(connection)
			print "--> [NXT_RC] Battery voltage:",
			print battery_voltage
		
		
		return(connection)
	
	
	##################################################################
	
	def connect_to_port(self, device_port):
	
		if isinstance(device_port, basestring):
			port = getattr(jaraco.nxt.messages.OutputPort, device_port)
		
		assert port in jaraco.nxt.messages.OutputPort.values()
		
		return(port)
	
	
	##################################################################
	
	def get_battery_voltage(self, connection):
		
		voltage = 'N/A'
		
		if connection != None:
			
			cmd = jaraco.nxt.messages.GetBatteryLevel()
			connection.send(cmd)
			
			response = connection.receive()
			voltage = response.get_voltage()
		
		
		return(voltage)
	
	
	##################################################################
	
	def get_status(self, connection):
		
		voltage = self.get_battery_voltage(connection)
		if type(voltage) == type (''):
			status = "%s volts" % voltage[:4]
		else:
			try:
				voltage = "%f" % voltage
				status = voltage[:4]
			except:
				status = 'N/A'
		
		return(status)
	
	
	##################################################################
	
	def cycle_motor(self, connection, motor_port='a'):
		
		"Turn the motor one direction, then the other, then stop it"
		
		port = self.connect_to_port(motor_port)
		cmd = jaraco.nxt.messages.SetOutputState(port, \
		                                         motor_on=True, \
		                                         set_power=60, \
		                   run_state=jaraco.nxt.messages.RunState.running)
		connection.send(cmd)
		
		time.sleep(2)
		
		cmd = jaraco.nxt.messages.SetOutputState(port, \
		                                         motor_on=True, \
		                                         set_power=-60, \
		                   run_state=jaraco.nxt.messages.RunState.running)
		connection.send(cmd)
		
		time.sleep(2)
		
		cmd = jaraco.nxt.messages.SetOutputState(port)
		connection.send(cmd)
	
	
	##################################################################
	
	def drive(self, connection, left_power, right_power, duration):
		
		"Operate both motors, each at certain power, for a certain duration"
		
		left_motor = self.connect_to_port(self.motor_port_left)
		right_motor = self.connect_to_port(self.motor_port_right)
		
		# If motors are mounted on the robot in reverse then all 
		# power settings need to be reversed
		if self.motors_mounted_backwards:
			left_power = -left_power
			right_power = -right_power
		
		# Issue operation settings to both motors
		cmd = jaraco.nxt.messages.SetOutputState(left_motor, \
															  motor_on=True, \
															  set_power=left_power, \
								 run_state=jaraco.nxt.messages.RunState.running)
		connection.send(cmd)
		
		cmd = jaraco.nxt.messages.SetOutputState(right_motor, \
															  motor_on=True, \
															  set_power=right_power, \
								 run_state=jaraco.nxt.messages.RunState.running)
		connection.send(cmd)
		
		# Continue operating motors while control program pauses
		if not VARIABLE_CONTROL_DURATION:
			time.sleep(duration)
			
			self.stop_motors(connection)
	
	
	##################################################################
	
	def stop_motors(self, connection):
		
		"Stop both motors"
		
		left_motor = self.connect_to_port(self.motor_port_left)
		right_motor = self.connect_to_port(self.motor_port_right)
		
		# Issue command to stop both motors
		cmd = jaraco.nxt.messages.SetOutputState(left_motor)
		connection.send(cmd)
		cmd = jaraco.nxt.messages.SetOutputState(right_motor)
		connection.send(cmd)
	
	
	##################################################################
	
	def drive_forward(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=2):
		
		"Drive the robot forward at a certain speed for a certain duration"
		
		self.drive(connection, power, power, duration)
	
	
	##################################################################
	
	def drive_reverse(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=2):
		
		"Drive the robot reverse at a certain speed for a certain duration"
		
		power = -power
		
		self.drive(connection, power, power, duration)
	
	
	##################################################################
	
	def turn_left_in_reverse(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=3):
		
		"Turn the robot counter-clockwise while backing up at a"
		" certain speed for a certain duration"
		
		left_power = -(power/3)
		right_power = -power
		
		self.drive(connection, left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_right_in_reverse(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=3):
		
		"Turn the robot clockwise while backing up at a"
		" certain speed for a certain duration"
		
		left_power = -power
		right_power = -(power/3)
		
		self.drive(connection, left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_left(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=2):
		
		"Turn the robot counter-clockwise at a"
		" certain speed for a certain duration"
		
		left_power = -(power/2)
		right_power = power
		
		self.drive(connection, left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_right(self, connection, power=DEFAULT_NXT_POWER_LEVEL, duration=2):
		
		"Turn the robot counter-clockwise at a"
		" certain speed for a certain duration"
		
		left_power = power
		right_power = -(power/2)
		
		self.drive(connection, left_power, right_power, duration)
	
	
	##################################################################
	
	def test_drive(self, connection):
		
		#self.cycle_motor(self.connection, motor_port='a')
		
		self.drive_forward(self.connection, power=100, duration=3)
		
		# half turn in reverse
		self.turn_right_in_reverse(self.connection, power=100, duration=2)
		
		self.drive_forward(self.connection, power=80, duration=2)
		
		# quarter turn left
		self.turn_left(self.connection, power=80, duration=2)
		
		self.drive_forward(self.connection, power=80, duration=1)
		
		# half turn right
		self.turn_right(self.connection, power=80, duration=2)
		
		self.drive_forward(self.connection, power=80, duration=1)
		
		self.drive_reverse(self.connection, power=80, duration=1)
	
	
	##################################################################
	
	def send_message(self, connection, message='test'):
		
		"send a message to nxt bluetooth stack of message box 1"
		
		cmd = jaraco.nxt.messages.MessageWrite(message)
		
		connection.send(cmd)
	
	
	##################################################################
	
	def run(self, command, power=DEFAULT_NXT_POWER_LEVEL):
		
		# If the LEGO Mindstorms NXT is instructed to drive with 
		# power less than 50% performance is so poor that we'd be
		# better off simply stopping the motors.
		if power < 50:
			command = 'stop_motors'
		
		if (command == 'drive_forward'):
			self.drive_forward(self.connection, power=power, duration=3)
		
		elif (command == 'drive_reverse'):
			self.drive_reverse(self.connection, power=power)
		
		elif (command == 'turn_left'):
			self.turn_left(self.connection, power=power)
		
		elif (command == 'turn_right'):
			self.turn_right(self.connection, power=power)
		
		elif (command == 'turn_left_in_reverse'):
			self.turn_left_in_reverse(self.connection, power=power)
		
		elif (command == 'turn_right_in_reverse'):
			self.turn_right_in_reverse(self.connection, power=power)
		
		elif (command == 'stop_motors'):
			self.stop_motors(self.connection)
		
		elif (command == 'test_drive'):
			self.test_drive(self.connection)
		
		elif (command == 'send_message_1'):
			self.send_message(self.connection, message='one')
		
		elif (command == 'send_message_2'):
			self.send_message(self.connection, message='two')
		
		elif (command == 'send_message_3'):
			self.send_message(self.connection ,message='three')
		
		elif (command == 'send_message_4'):
			self.send_message(self.connection, message='four')
		
		elif (command == 'send_message_5'):
			self.send_message(self.connection, message='five')
		
		elif (command == 'send_message_6'):
			self.send_message(self.connection, message='six')
	
	
	##################################################################
	
	def stop(self):
		
		self.connection.close()


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Collect default settings and command line parameters
	device = BLUETOOTH_DEVICE
	command = DEFAULT_RC_COMMAND
	
	for each in sys.argv:
		
		if each.startswith("--device="):
			device = each[ len("--device="): ]
		elif each.startswith("--command="):
			command = each[ len("--command="): ]
	
	
	rc = puzzlebox_brainstorms_nxt_control(device=device, command=command, DEBUG=DEBUG)
	
	if rc.connection == None:
		sys.exit()
	
	rc.run(rc.command)
	rc.stop()

