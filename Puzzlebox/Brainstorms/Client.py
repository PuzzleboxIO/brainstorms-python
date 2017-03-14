#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Network - Client
#
# Copyright Puzzlebox Productions, LLC (2010-2011)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2011.12.05

"""

import os, sys
import signal

import Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		import PySide as PyQt4
		from PySide import QtCore, QtGui, QtNetwork
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Brainstorms:Client] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:Client] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork

#from PyQt4 import QtCore, QtGui, QtNetwork

import simplejson as json

import Configuration as configuration
#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

SERVER_HOST = configuration.BRAINSTORMS_SERVER_HOST
SERVER_PORT = configuration.BRAINSTORMS_SERVER_PORT

CLIENT_NO_REPLY_WAIT = configuration.CLIENT_NO_REPLY_WAIT * 1000

DELIMITER = configuration.BRAINSTORMS_DELIMITER

DEFAULT_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

DEFAULT_NXT_POWER_LEVEL = configuration.DEFAULT_NXT_POWER_LEVEL
NXT_DEFAULT_RC_COMMAND = configuration.NXT_DEFAULT_RC_COMMAND

DEFAULT_ROBOT_TYPE = 'NXT'

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_network_client:
	
	def __init__(self, log, \
		          server_host=SERVER_HOST, \
		          server_port=SERVER_PORT, \
		          device_address=DEFAULT_DEVICE, \
		          robot_type=DEFAULT_ROBOT_TYPE, \
		          DEBUG=DEBUG, \
		          parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent=parent
		
		self.server_host = server_host
		self.server_port = server_port
		
		self.robot_type = robot_type
		
		self.configureNetwork()
	
	
	##################################################################
	
	def configureNetwork(self):
	
		#self.blockSize = 0
		self.socket = QtNetwork.QTcpSocket()
		self.socket.name = 'Brainstorms Client'
		
		self.socket.readyRead.connect(self.printReply)
		self.socket.error.connect(self.displayError)
	
	
	##################################################################
	
	def printReply(self):
		
		socket_buffer = self.socket.readAll()
		
		for packet in socket_buffer.split(DELIMITER):
			
			if packet != '':
				
				try:
					data = json.loads(packet.data())
				except:
					data = packet
				
				if self.DEBUG:
					print "--> [%s] Received:" % self.socket.name,
					print data
				
				
				# If Brainstorms server is connected to a LEGO Mindstorms NXT
				# robot, it will send back a voltage measurement which
				# can be presented to the user through the client interface
				if ((self.parent != None) and \
					 (type(data) == type({})) and \
					 ('status' in data.keys())):
					
					status = str(data['status'])
					
					#if (status.find('N/A') == -1):
						#status = status[:4]
						#status = "%s volts" % status
					
					label = 'Status: %s' % status
					
					self.parent.textLabelRobotStatus.setText(label)
	
	
	##################################################################
	
	def displayError(self, socketError):
		
		if self.DEBUG:
			if (socketError != QtNetwork.QAbstractSocket.RemoteHostClosedError):
				print "ERROR [%s]:" % self.socket.name,
				print self.socket.errorString()
		
		
		if (self.parent != None):
		
			if socketError == QtNetwork.QAbstractSocket.RemoteHostClosedError:
				pass
			
			elif socketError == QtNetwork.QAbstractSocket.HostNotFoundError:
				QtGui.QMessageBox.information(self.parent, \
					                           self.socket.name, \
					   "The server host was not found. Please check the host name and "
					   "port settings.")
			
			elif socketError == QtNetwork.QAbstractSocket.ConnectionRefusedError:
				QtGui.QMessageBox.information(self.parent, \
					                           self.socket.name,
					   "The server connection was refused by the peer. Make sure the "
					   "server is running, and check that the host name "
					   "and port settings are correct.")
			
			else:
				QtGui.QMessageBox.information(self.parent, \
					                           self.socket.name, \
					   "The following error occurred: %s." % \
					   self.socket.errorString())
	
	
	##################################################################
	
	def sendCommand(self, command, power=DEFAULT_NXT_POWER_LEVEL, \
	                device_address=None, default_data={}):
		
		packet = default_data
		packet['command'] = command
		packet['power'] = power
		packet['robot_type'] = self.robot_type
		
		if device_address != None:
			packet['device_address'] = str(device_address)
		
		if self.DEBUG:
			print "<-- [%s] Sending:" % self.socket.name,
			print packet
		
		self.socket.abort()
		self.socket.connectToHost(self.server_host, self.server_port)
		
		data = json.dumps(packet)
		
		if self.socket.waitForConnected(CLIENT_NO_REPLY_WAIT):
			self.socket.write(data)
		else:
			if self.DEBUG:
				print "WARNING [%s] Timeout waiting for connection to server" % \
				   self.socket.name


#####################################################################
# Command line class
#####################################################################

class puzzlebox_brainstorms_network_client_command_line( \
	      puzzlebox_brainstorms_network_client):
	
	def __init__(self, log, \
		          command_parameters, \
		          server_host=SERVER_HOST, \
		          server_port=SERVER_PORT, \
		          DEBUG=DEBUG):
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent = None
		
		self.command_parameters = command_parameters
		self.server_host = server_host
		self.server_port = server_port
		
		self.configureNetwork()
		
		self.execute_command_line()
	
	
	##################################################################
	
	def execute_command_line(self):
		
		(command) = self.parse_command_line(self.command_parameters)
		
		if (command != None):
		
			self.sendCommand(command)
		
			self.socket.waitForReadyRead(CLIENT_NO_REPLY_WAIT)
	
	
	##################################################################
	
	def parse_command_line(self, command_parameters):
		
		try:
			command = command_parameters[0]
		except:
			command = NXT_DEFAULT_RC_COMMAND
		
		
		return(command)


#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client')
	log = None
	
	command_parameters = sys.argv[1:]
	
	#log.info("Command parameters: %s" % command_parameters)
	
	client = puzzlebox_brainstorms_network_client_command_line(log, \
	            command_parameters, \
	            server_host=SERVER_HOST, \
	            server_port=SERVER_PORT, \
	            DEBUG=DEBUG)

