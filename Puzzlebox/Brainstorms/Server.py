#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Network - Server
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2012.04.16

"""

import os, sys
import signal

import simplejson as json

import Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		import PySide as PyQt4
		from PySide import QtCore, QtNetwork
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Brainstorms:Server] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:Server] Using PyQt4 module"
	from PyQt4 import QtCore, QtNetwork


try:
	import NXT_Control as nxt_control
except Exception, e:
	 print "ERROR: Exception importing NXT_Control:",
	 print e

try:
	import iRobot_Control as irobot_control
except Exception, e:
	 print "ERROR: Exception importing iRobot_Control:",
	 print e

try:
	import RC_Car_Control as rc_car_control
except Exception, e:
	 print "ERROR: Exception importing RC_Car_Control:",
	 print e

#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

SERVER_INTERFACE = configuration.BRAINSTORMS_SERVER_INTERFACE
SERVER_PORT = configuration.BRAINSTORMS_SERVER_PORT

CLIENT_NO_REPLY_WAIT = configuration.CLIENT_NO_REPLY_WAIT * 1000

DELIMITER = configuration.BRAINSTORMS_DELIMITER

DEFAULT_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

VARIABLE_CONTROL_DURATION = configuration.BRAINSTORMS_VARIABLE_CONTROL_DURATION

MOTORS_MOUNTED_BACKWARDS = configuration.NXT_MOTORS_MOUNTED_BACKWARDS
MOTOR_PORT_RIGHT = configuration.NXT_MOTOR_PORT_RIGHT
MOTOR_PORT_LEFT = configuration.NXT_MOTOR_PORT_LEFT

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_network_server:
	
	def __init__(self, log, \
		          server_interface=SERVER_INTERFACE, \
		          server_port=SERVER_PORT, \
		          embedded_mode=False, \
		          robot_type=None, \
		          DEBUG=DEBUG, \
		          parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		
		self.server_interface = server_interface
		self.server_port = server_port
		
		self.embedded_mode=embedded_mode
		
		self.configureNetwork()
		
		self.robot_type = robot_type
		
		self.motors_mounted_backwards = MOTORS_MOUNTED_BACKWARDS
		self.motor_port_right = MOTOR_PORT_RIGHT
		self.motor_port_left = MOTOR_PORT_LEFT
		
		self.device_address = None
		
		self.rc = None
	
	
	##################################################################
	
	def configureNetwork(self):
	
		#self.blockSize = 0
		self.socket = QtNetwork.QTcpServer()
		self.socket.name = 'Brainstorms Server'
		
		if self.DEBUG:
			print "<---- [%s] Initializing server on %s:%i" % \
				(self.socket.name, self.server_interface, self.server_port)
	
		if (self.server_interface == ''):
			address=QtNetwork.QHostAddress.Any
		else:
			address=address=self.server_interface
		
		port = self.server_port
		
		result = self.socket.listen(address, port)
		
		if not result:
			if self.DEBUG:
				print "ERROR [%s] Unable to start the server:" % self.socket.name,
				print self.socket.errorString()
				
			self.socket.close()
			return
		
		
		self.socket.newConnection.connect(self.processConnection)
	
	
	##################################################################
	
	def processConnection(self):
		
		if self.DEBUG:
			print "--> [%s]: Client connected" % self.socket.name
		
		clientConnection = self.socket.nextPendingConnection()
		clientConnection.disconnected.connect(clientConnection.deleteLater)
		
		if (self.embedded_mode):
			
			# Only one client connection to server will work in embedded mode
			self.clientConnection = clientConnection
			clientConnection.readyRead.connect(self.processData)
		
		
		else:
			
			if not clientConnection.waitForReadyRead(CLIENT_NO_REPLY_WAIT):
				if self.DEBUG:
					print "WARNING [%s] Timeout waiting for client to transmit data" % \
						self.socket.name
					#print "State:",
					#print clientConnection.state()
				clientConnection.disconnectFromHost()
				return
			
			
			self.processData(clientConnection)
			
			#clientConnection.disconnectFromHost()
	
	
	##################################################################
	
	def processData(self, clientConnection=None):
		
		if (clientConnection == None):
			clientConnection = self.clientConnection
		
		socket_buffer = clientConnection.readAll()
		
		for packet in socket_buffer.split(DELIMITER):
			
			if packet != '':
				
				try:
					data = json.loads(packet.data())
				except:
					data = packet
				
				if self.DEBUG:
					print "--> [%s] Received:" % self.socket.name,
					print data
				
				response = self.processCommand(data)
				
				if response != None:
					
					data = json.dumps(response)
					
					
					if clientConnection.waitForConnected(CLIENT_NO_REPLY_WAIT):
						
						if self.DEBUG:
							print "<-- [%s] Sending:" % self.socket.name,
							print data
						
						clientConnection.write(data)
	
	
	##################################################################
	
	def processCommand(self, data):
		
		response = {}
		
		if 'robot_type' in data.keys():
			self.robot_type = data['robot_type']
		
		
		if self.robot_type == 'NXT':
			
			if 'motors_mounted_backwards' in data.keys():
				self.motors_mounted_backwards = data['motors_mounted_backwards']
				if (self.rc != None):
					self.rc.motors_mounted_backwards = self.motors_mounted_backwards
				return('OK')
			
			elif 'motor_port_right' in data.keys():
				self.motor_port_right = data['motor_port_right']
				if (self.rc != None):
					self.rc.motor_port_right = self.motor_port_right
				return('OK')
			
			elif 'motor_port_left' in data.keys():
				self.motor_port_left = data['motor_port_left']
				if (self.rc != None):
					self.rc.motor_port_left = self.motor_port_left
				return('OK')
		
		
		if ((not VARIABLE_CONTROL_DURATION) or \
		    (self.robot_type == 'iRobot')):
			
			# Variable Control Duration is used to configure whether or
			# not a robot will follow its a direction command continuously until
			# a "stop" or different direction is received. If disabled or set to
			# "false" then the robot will normally carry out a direction time
			# for a brief pre-set period then stop automatically.
			
			response['status'] = self.executeCommand(data['command'], data['power'])
		
		
		else:
			
			if ((self.rc == None) or \
				 (self.rc.connection == None) or \
			         (self.device_address == None)):
				
				if ('device_address' in data.keys()):
					self.device_address = data['device_address']
				else:
					self.device_address = DEFAULT_DEVICE
				
				if self.robot_type == 'iRobot':
					self.rc = irobot_control.irobot_control(device=self.device_address)
				elif self.robot_type == 'RC Car':
					self.rc = rc_car_control.puzzlebox_brainstorms_rc_car_control( \
						          device_address=self.device_address, \
						          DEBUG=DEBUG)
				else:
					self.rc = nxt_control.puzzlebox_brainstorms_nxt_control( \
					             device_address=self.device_address, \
					             motors_mounted_backwards=self.motors_mounted_backwards, \
					             motor_port_right=self.motor_port_right, \
					             motor_port_left=self.motor_port_left, \
					             DEBUG=DEBUG)
			
			
			if self.rc.connection != None:
				
				self.rc.run(data['command'], data['power'])
				response['status'] = self.rc.get_status(self.rc.connection)
			
			else:
				
				self.rc = None
				response = {}
				response['status'] = 'STATUS N/A'
		
		
		return(response)
	
	
	##################################################################
	
	def executeCommand(self, command):
		
		status = 'N/A'
		
		if self.robot_type == 'iRobot':
			
			rc = irobot_control.irobot_control( \
			        device_address=self.device_address, \
			        command=command)
		
		elif self.robot_type == 'RC Car':
			
			rc = rc_car_control.puzzlebox_brainstorms_rc_car_control( \
			        device_address=self.device_address, \
			        command=command)
		
		else:
		
			rc = nxt_control.puzzlebox_brainstorms_nxt_control( \
				     device_address=self.device_address, \
				     command=command, \
				     motors_mounted_backwards=self.motors_mounted_backwards, \
				     motor_port_right=self.motor_port_right, \
				     motor_port_left=self.motor_port_left, \
				     DEBUG=DEBUG)
		
		
		if rc.connection != None:
			rc.run(rc.command)
			rc.stop()
			
			status = rc.get_status(rc.connection)
		
		
		return(status)


#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='server_brainstorms')
	log = None
	
	# Collect default settings and command line parameters
	server_interface = SERVER_INTERFACE
	server_port = SERVER_PORT
	
	for each in sys.argv:
		
		if each.startswith("--interface="):
			server_interface = each[ len("--interface="): ]
		if each.startswith("--port="):
			server_port = each[ len("--port="): ]
	
	
	app = QtCore.QCoreApplication(sys.argv)
	
	server = puzzlebox_brainstorms_network_server(log, \
	                                              server_interface, \
	                                              server_port, \
	                                              embedded_mode=False, \
	                                              DEBUG=DEBUG)
	
	sys.exit(app.exec_())

