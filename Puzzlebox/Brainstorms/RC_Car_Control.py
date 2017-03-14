#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - RC Car Control
#
# Copyright Puzzlebox Productions, LLC (2011)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """
Last Update: 2011.06.20

"""

import sys, string, time
import serial

import Configuration as configuration

#####################################################################
# Globals
#####################################################################

DEBUG = 1

VARIABLE_CONTROL_DURATION = configuration.BRAINSTORMS_VARIABLE_CONTROL_DURATION

DEFAULT_COMMAND = 'stop_motors'
DEFAULT_SERIAL_DEVICE = '/dev/ttyACM0'

DEFAULT_RC_CAR_POWER_LEVEL = configuration.DEFAULT_RC_CAR_POWER_LEVEL

ARDUINO_INITIALIZATION_TIME = 2

THROTTLE_POWER_MODIFIER = 0.25
STEERING_POWER_MODIFIER = 0.75

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_rc_car_control:
	
	def __init__(self, \
		          device_address=DEFAULT_SERIAL_DEVICE, \
		          command=DEFAULT_COMMAND, \
		          DEBUG=DEBUG):
		
		self.DEBUG = DEBUG
		
		self.device_address = device_address
		self.command = command
		
		self.device = None
		
		try:
			self.initializeSerial()
		except Exception, e:
			if self.DEBUG:
				print "<-- [RC_CAR] Connection failed to RC Car device [%s]" % self.device
				print "ERROR [RC_CAR]:",
				print e
		
		self.connection = self.device
	
	
	##################################################################
	
	def initializeSerial(self):
		
		baudrate = 9600
		bytesize = 8
		parity = 'NONE'
		stopbits = 1
		software_flow_control = 'f'
		rts_cts_flow_control = 't'
		#timeout = 15
		timeout = 5
		
		# convert bytesize
		if (bytesize == 5):
			init_byte_size = serial.FIVEBITS
		elif (bytesize == 6):
			init_byte_size = serial.SIXBITS
		elif (bytesize == 7):
			init_byte_size = serial.SEVENBITS
		elif (bytesize == 8):
			init_byte_size = serial.EIGHTBITS
		else:
			#self.log.perror("Invalid value for %s modem byte size! Using default (8)" % modem_type)
			init_byte_size = serial.EIGHTBITS
		
		# convert parity
		if (parity == 'NONE'):
			init_parity = serial.PARITY_NONE
		elif (parity == 'EVEN'):
			init_parity = serial.PARITY_EVEN
		elif (parity == 'ODD'):
			init_parity = serial.PARITY_ODD
		else:
			#self.log.perror("Invalid value for %s modem parity! Using default (NONE)" % modem_type)
			init_parity = serial.PARITY_NONE
		
		# convert stopbits
		if (stopbits == 1):
			init_stopbits = serial.STOPBITS_ONE
		elif (stopbits == 2):
			init_stopbits = serial.STOPBITS_TWO
		else:
			#self.log.perror("Invalid value for %s modem stopbits! Using default (8)" % modem_type)
			init_byte_size = serial.STOPBITS_ONE
		
		# convert software flow control
		if (software_flow_control == 't'):
			init_software_flow_control = 1
		else:
			init_software_flow_control = 0
		
		# convert rts cts flow control
		if (rts_cts_flow_control == 't'):
			init_rts_cts_flow_control = 1
		else:
			init_rts_cts_flow_control = 0
		
		self.device = serial.Serial(port = self.device_address, \
										baudrate = baudrate, \
										bytesize = init_byte_size, \
										parity = init_parity, \
										stopbits = init_stopbits, \
										xonxoff = init_software_flow_control, \
										rtscts = init_rts_cts_flow_control, \
										timeout = timeout)
		
		
		self.stop_motors()
		
		time.sleep(ARDUINO_INITIALIZATION_TIME)
	
	
	##################################################################
	
	def get_status(self, connection):
		
		#status = self.get_battery_voltage(connection)
		status = 'Connected'
		
		return(status)
	
	
	##################################################################
	
	def drive(self, throttle, steering, duration):
		
		throttle = int(throttle * THROTTLE_POWER_MODIFIER)
		steering = int(steering * STEERING_POWER_MODIFIER)
		
		if self.DEBUG:
			print '--> [RC_CAR] Drive: Throttle [%i] Steering [%i],' % \
			         (throttle, steering)
		
		
		if throttle >= 0:
			throttle = '+%i' % throttle
			while len(throttle) < 4:
				throttle = throttle.replace('+', '+0')
		else:
			throttle = '%i' % throttle
			while len(throttle) < 4:
				throttle = throttle.replace('-', '-0')
		
		if steering >= 0:
			steering = '+%i' % steering
			while len(steering) < 4:
				steering = steering.replace('+', '+0')
		else:
			steering = '%i' % steering
			while len(steering) < 4:
				steering = steering.replace('-', '-0')
		
		
		command = "!%s,%s" % (throttle, steering)
		
		if self.DEBUG:
			print '("%s")' % command
		
		# Issue operation settings to RC Car
		self.device.write(command)
		
		
		# Continue operating motors while control program pauses
		if not VARIABLE_CONTROL_DURATION:
			time.sleep(duration)
			
			self.stop_motors()
	
	
	##################################################################
	
	def stop_motors(self):
		
		"Stop both axis motors"
		
		# Issue command to stop both motors
		if self.DEBUG:
			print '--> [RC_CAR] Stop ("!+000,+000")'
		
		self.device.write("!+000,+000")
	
	
	##################################################################
	
	#def neutral(self):
		
		#self.stop_motors()
	
	
	##################################################################
	
	def drive_forward(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=2):
		
		"Drive the robot forward at a certain speed for a certain duration"
		
		throttle = power
		steering = 0
		
		self.drive(throttle, steering, duration)
	
	
	##################################################################
	
	def drive_reverse(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=2):
		
		"Drive the robot reverse at a certain speed for a certain duration"
		
		throttle = -power
		steering = 0
		
		self.drive(throttle, steering, duration)
	
	
	##################################################################
	
	def turn_left_in_reverse(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=3):
		
		"Turn the robot counter-clockwise while backing up at a"
		" certain speed for a certain duration"
		
		left_power = -(power/3)
		right_power = -power
		
		#self.drive(left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_right_in_reverse(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=3):
		
		"Turn the robot clockwise while backing up at a"
		" certain speed for a certain duration"
		
		left_power = -power
		right_power = -(power/3)
		
		#self.drive(left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_left(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=2):
		
		"Turn the robot counter-clockwise at a"
		" certain speed for a certain duration"
		
		left_power = -(power/2)
		right_power = power
		
		#self.drive(left_power, right_power, duration)
	
	
	##################################################################
	
	def turn_right(self, power=DEFAULT_RC_CAR_POWER_LEVEL, duration=2):
		
		"Turn the robot counter-clockwise at a"
		" certain speed for a certain duration"
		
		left_power = power
		right_power = -(power/2)
		
		#self.drive(left_power, right_power, duration)
	
	
	##################################################################
	
	def run(self, command, power=DEFAULT_RC_CAR_POWER_LEVEL):
		
		# If the RC Car is instructed to drive with power less than
		# a certain threshold performance is so poor that we'd be
		# better off simply stopping the motors.
		if power < 50:
			command = 'stop_motors'
		
		if (command == 'drive_forward'):
			self.drive_forward(power=power, duration=3)
		
		elif (command == 'drive_reverse'):
			self.drive_reverse(power=power)
		
		elif (command == 'turn_left'):
			self.turn_left(power=power)
		
		elif (command == 'turn_right'):
			self.turn_right(power=power)
		
		elif (command == 'turn_left_in_reverse'):
			self.turn_left_in_reverse(power=power)
		
		elif (command == 'turn_right_in_reverse'):
			self.turn_right_in_reverse(power=power)
		
		elif (command == 'stop_motors'):
			self.stop_motors()
	
	
	##################################################################
	
	def stop(self):
		
		self.device.close()
	
	
	##################################################################
	
	#def run(self):
		
		#if self.DEBUG:
			#print "<---- [%s] Main thread running" % "RC Car Control"
		
		##self.processCommand()
		
		#self.exec_()
	
	
	##################################################################
	
	#def exitThread(self, callThreadQuit=True):
		
		#try:
			#self.device.stop()
		#except:
			#pass
		
		##self.wait()
		#if callThreadQuit:
			#QtCore.QThread.quit(self)


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	# Collect default settings and command line parameters
	device = DEFAULT_SERIAL_DEVICE
	command = DEFAULT_COMMAND
	
	for each in sys.argv:
		
		if each.startswith("--device="):
			device = each[ len("--device="): ]
		elif each.startswith("--command="):
			command = each[ len("--command="): ]
	
	
	#rc = puzzlebox_brainstorms_nxt_control(device=device, command=command, DEBUG=DEBUG)
	
	#if rc.connection == None:
		#sys.exit()
	
	#rc.run(rc.command)
	#rc.stop()
	
	
	app = QtCore.QCoreApplication(sys.argv)
	
	rc_car = puzzlebox_brainstorms_rc_car_control( \
	                device_address=device, \
	                command=command, \
	                DEBUG=DEBUG)
	
	rc_car.start()
	
	sys.exit(app.exec_())
