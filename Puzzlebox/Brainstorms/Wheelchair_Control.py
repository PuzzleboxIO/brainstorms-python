#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Wheelchair Control
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """
Last Update: 2012.08.20
"""

import sys
import time
import signal
import serial
if (sys.platform != 'win32'):
	import tty, termios # console()
        import select # console()

import Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		#import PySide as PyQt4
		from PySide import QtCore
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Brainstorms:Wheelchair_Control] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:Wheelchair_Control] Using PyQt4 module"
	from PyQt4 import QtCore


#####################################################################
# Globals
#####################################################################

DEBUG = 1

DEFAULT_COMMAND = 'console'
#DEFAULT_COMMAND = 'controller'
DEFAULT_SERIAL_DEVICE = '/dev/arduino1'
#DEFAULT_SERIAL_DEVICE = '/dev/ttyUSB0'
#DEFAULT_SERIAL_DEVICE = '/dev/ttyACM0'
#DEFAULT_SERIAL_DEVICE = '/dev/ttyACM1'

#DEFAULT_SERIAL_BAUD = 9600
DEFAULT_SERIAL_BAUD = 57600

#try:
	##PORT = serial.Serial("/dev/arduino1",baudrate=57600,bytesize=serial.EIGHTBITS)
	##PORT = serial.Serial("/dev/ttyUSB0",baudrate=57600,bytesize=serial.EIGHTBITS)
	#PORT = serial.Serial(DEFAULT_SERIAL_DEVICE,baudrate=57600,bytesize=serial.EIGHTBITS) # controller()
#except:
	#pass

DEFAULT_WHEELCHAIR_SPEED = 0 # tracks numeric value
DEFAULT_WHEELCHAIR_COMMAND = 'stop'

#ARDUINO_INITIALIZATION_TIME = 2
ARDUINO_INITIALIZATION_TIME = 5 # increased 2012.08.17
COMMAND_CHARACTER = 'x'
GUI_SLEEP_TIMER = 1 * 100 # 100ms

COMMAND_POWER_ON = 'Pz'
COMMAND_POWER_OFF = 'Pa'
COMMAND_STOP = 'SS'
DEFAULT_DIRECTION = 'F'
DEFAULT_SPEED = 6
COMMAND_DEFAULT = DEFAULT_DIRECTION + chr(int(DEFAULT_SPEED)*255/9) + COMMAND_POWER_ON

#WHEELCHAIR_COMMANDS = {
	#1: { # speed
		#'forward': '00110001',
		#'reverse': '00111011',
		#'left': '10110011',
		#'right': '00010011',
		#'stop': '00110011', 
	#},
	#2: { # speed
		#'forward': '00110010',
		#'reverse': '00110111',
##		'left': '01110011',  # Turning in Speed 2 is disproportionately fast
##		'right': '00100011', # Turning in Speed 2 is disproportionately fast
		#'left': '10110011',  # Turn Speed 1
		#'right': '00010011', # Turn Speed 1
		#'stop': '00110011', 
	#},
	#3: { # speed
		#'forward': '00110000',
		#'reverse': '00111111',
##		'left': '11110011',  # Turning in Speed 3 is too fast
##		'right': '00000011', # Turning in Speed 3 is too fast
		#'left': '01110011',  # Turn Speed 2
		#'right': '00100011', # Turn Speed 2
		#'stop': '00110011', 
	#},
#}

CONTROLS = {
	'forward': 'F',
	'reverse': 'B',
	'fwd':     'F',
	'rev':     'B',
	'right':   'R',
	'left':    'L',
}

MOVE_COMMANDS ={
	' ' : 'stop',
	'i' : 'fwd',
	'm' : 'rev',
	'j' : 'left',
	'k' : 'right',
}

SPEED_COMMANDS = {
	's' : -1,
	'd' : +1,
	'f' : -25,
	'g' : +25,
}

DIGITS = map(str,range(10))

STOP_TIME = 0
STOP_INTERVAL = 0.2
ALARM_INTERVAL = 0.1

#STEERING_SENSITIVITY = 0.5   # multiplier for left/right commands
STEERING_SENSITIVITY = 1      # multiplier for left/right commands (updated resistor 2012.08.15)


#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_wheelchair_control(QtCore.QThread):
	
	def __init__(self, \
	             device_address=DEFAULT_SERIAL_DEVICE, \
	             command=DEFAULT_COMMAND, \
	             DEBUG=DEBUG, \
	             parent=None):
		
		QtCore.QThread.__init__(self, parent)
		
		self.log = None
		self.DEBUG = DEBUG
		self.parent = parent
		
		self.device_address = device_address
		self.command = command
		
		self.wheelchair_speed = DEFAULT_WHEELCHAIR_SPEED
		self.wheelchair_command = DEFAULT_WHEELCHAIR_COMMAND
		
		self.device = None
		self.previous_serial_settings = None
		self.initializeSerial()
		
		self.keep_running = True
		
		self.speed = None
		self.setSpeed(0)
	
	
	##################################################################
	
	def initializeSerial(self):
		
		try:
			self.previous_serial_settings = termios.tcgetattr(sys.stdin)
		except Exception, e:
			print "WARNING: failed to retrieve previous serial settings"
		
		baudrate = DEFAULT_SERIAL_BAUD
		bytesize = 8
		parity = 'NONE'
		stopbits = 1
		software_flow_control = 'f'
		#rts_cts_flow_control = 't'
		rts_cts_flow_control = 'f' # no hardward flow control for McHawking robot
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
		
		self.writeStop()
		
		time.sleep(2) # pause for one second before sending anything further
		
		self.writeCommand() # send forward command once to activate
		
		#time.sleep(ARDUINO_INITIALIZATION_TIME)
	
	
	##################################################################
	
	def writeStop(self):
		if self.DEBUG:
			print "Writing:",
			print COMMAND_STOP + COMMAND_POWER_ON
		self.device.write(COMMAND_STOP + COMMAND_POWER_ON)
		#debug.write(COMMAND_STOP + COMMAND_POWER_ON)

	def writeCommand(self):
		if self.DEBUG:
			print "Writing:",
			print COMMAND_DEFAULT
		self.device.write(COMMAND_DEFAULT)
		#debug.write(COMMAND_DEFAULT)

	def writeKeepAlive(self):
		if self.DEBUG > 2:
			print "Writing:",
			print COMMAND_POWER_ON
		self.device.write(COMMAND_POWER_ON)
		#debug.write(COMMAND_POWER_ON)
	
	
	##################################################################
	
	def sendCommand(self, speed, command):
		
		
		if self.DEBUG:
			print "DEBUG [Brainstorms:Wheelchair_Control]: sendCommand( speed:",
			print speed,
			print " command:",
			print command,
			print ")"
		
		
		if speed != self.wheelchair_speed:
			#setSpeed(speed)
			#self.handleCommand(speed)
			self.setSpeed(int(speed)*255/9)
		
		#output = '%s%s' % (COMMAND_CHARACTER, \
			#WHEELCHAIR_COMMANDS[self.speed][command])
		
		
		#self.device.write(output)
		
		
		if command in CONTROLS.keys():
			self.moveBot(command)
		
		
		else:
			self.wheelchair_command = 'stop'
		
		
		#if self.DEBUG:
			#print "--> Wheelchair Command: %s (Speed %i) [%s]" % \
			   #(command, self.speed, output)
		
		
		self.wheelchair_speed = speed
		#self.wheelchair_command = command
	
	
	##################################################################
	
	def setOutput(self, data):
		
		if self.DEBUG:
			print "DEBUG [Brainstorms:Wheelchair_Control]: write: %sPz" % data
		
		#self.device.write(data)
		#self.device.write("Pz")
		
		output = data + "Pz"
		
		self.wheelchair_command = output
	#	print 'Output set to:', data[0], ord(data[1])
	#       printHelp()
	
	
	def setDrive(self, value):
		if value == 'A':
			self.setOutput('DA')
		if value == 'B':
			self.setOutput('DB')
	
	
	def moveBot(self, dir):
		
		if (dir in ['left','right']):
			output = CONTROLS[dir] + chr(int(self.speed * STEERING_SENSITIVITY))
		else:
			output = CONTROLS[dir] + chr(self.speed)
		
		self.setOutput(output)
	
	
	def stopBot(self):
		self.setOutput('SS')
	
	
	def setSpeed(self, value):
		new_speed = value
		if new_speed > 255:
			new_speed = 255
		if new_speed < 0:
			new_speed = 0
		
		self.speed = new_speed
		
		print 'speed:', self.speed, '/ 255'
	
	
	def handleCommand(self, cmd):
		if cmd in DIGITS: # 0-9
			self.setSpeed(int(cmd)*255/9)
		if cmd in SPEED_COMMANDS.keys():
			self.setSpeed(self.speed + SPEED_COMMANDS[cmd])
		elif cmd in MOVE_COMMANDS.keys():
			if MOVE_COMMANDS[cmd] == 'stop':
				self.stopBot()
			else:
				print MOVE_COMMANDS[cmd]
				self.moveBot(MOVE_COMMANDS[cmd])
		#elif cmd == 'w':
			#rockets.up()
		#elif cmd == 'e':
			#rockets.down()
		#elif cmd == 'q':
			#rockets.left()
		#elif cmd == 'r':
			 #rockets.right()	
		#elif cmd == 't':
			#rockets.laser()
		#elif cmd == 'y':
			#rockets.fire()
		elif cmd == 'a':
			self.setDrive('A')
		elif cmd == 'b':
			self.setDrive('B')
	
	 
	def printHelp(self):
		print 'commands: '
		print 'i j k l to move, SPACE = stop, x = quit'
		print 's d f g or 0-9 to adjust speed between 0 and 255.'
	
	
	def isData(self):
		return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
	
	
	#################################################################
	
	def consoleControl(self):
		
		print "DEBUG: consoleControl()"
		
		if (sys.platform == 'win32'):
			if self.DEBUG:
				print "---> Wheelchair Control: Console mode unavailable under Windows"
			
			self.exitThread()
		
		
		MYGETCH = Getch()
		
		while True:
			
			self.writeKeepAlive()
			
			cmd = MYGETCH()
			#cmd = ""
			#cmd = sys.stdin.read(1)
			
			#if self.isData():
			if True:
				if cmd == 'x':
					break
				
				if len(cmd) > 0:
					self.handleCommand(cmd)
					#if cmd == '?':
					self.printHelp()
			
			if self.device.inWaiting() > 0:
				print self.device.readline().strip()
			
			
			#QtCore.QThread.msleep(GUI_SLEEP_TIMER)

	
	
	##################################################################
	
	def guiControl(self):
		
		while self.keep_running:
			
			self.writeKeepAlive()
			
			if self.wheelchair_command != 'stop':
				if self.DEBUG:
					print "Wrote to device:",
					print self.wheelchair_command
				self.device.write(self.wheelchair_command)
			
			
			if self.device.inWaiting() > 0:
				line = self.device.readline()
				
				line = line.strip()
				
				if self.DEBUG:
					print "Read from device:",
					print line
			
			
			QtCore.QThread.msleep(GUI_SLEEP_TIMER)
	
	
	##################################################################
	
	def processCommand(self):
		
		if (self.command == 'console'):
			self.consoleControl()
		
		elif (self.command == 'gui'):
			self.guiControl()
		
		else:
			self.guiControl()
	
	
	##################################################################
	
	def run(self):
		
		if self.DEBUG:
			print "<---- [%s] Main thread running" % "Wheelchair Control"
		
		
		self.processCommand()
		
		self.exec_()
	
	
	##################################################################
	
	def stop(self):
		
		self.keep_running = False
	
	
	##################################################################
	
	def exitThread(self, callThreadQuit=True):
		
		print "DEBUG: exitThread()"
		
		try:
			self.stopBot()
		except:
			pass
		
		if self.previous_serial_settings != None:
			try:
				termios.tcsetattr(sys.stdin, \
				                  termios.TCSADRAIN, \
				                  self.previous_serial_settings)
			except Exception, e:
				print "WARNING: failed to set previous serial settings"
		
		#self.wait()
		if callThreadQuit:
			QtCore.QThread.quit(self)


#####################################################################
#####################################################################

class Getch:
	
	def __init__(self):
		import tty, sys
	
	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


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
	
	
	app = QtCore.QCoreApplication(sys.argv)
	
	wheelchair = puzzlebox_brainstorms_wheelchair_control( \
	                device_address=device, \
	                command=command, \
	                DEBUG=DEBUG)
	
	wheelchair.start()
	
	sys.exit(app.exec_())
