#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Network - Client - Thinkgear
#
# Copyright Puzzlebox Productions, LLC (2010)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html
#
# Last Update: 2010.07.10
#
#####################################################################

import os, sys
import signal

import Puzzlebox.Brainstorms.Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		import PySide as PyQt4
		from PySide import QtCore, QtNetwork
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Brainstorms:ThinkGear:Client] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:ThinkGear:Client] Using PyQt4 module"
	from PyQt4 import QtCore, QtNetwork

#try:
	#import PySide as PyQt4
	#from PySide import QtCore, QtNetwork
#except:
	#print "Using PyQt4 module"
	#from PyQt4 import QtCore, QtNetwork
#else:
	#print "Using PySide module"

#from PyQt4 import QtCore, QtNetwork

import simplejson as json

#import Puzzlebox.Brainstorms.Configuration as configuration
#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

SERVER_HOST = configuration.THINKGEAR_SERVER_HOST
SERVER_PORT = configuration.THINKGEAR_SERVER_PORT

CLIENT_NO_REPLY_WAIT = configuration.CLIENT_NO_REPLY_WAIT * 1000

DELIMITER = configuration.THINKGEAR_DELIMITER

THINKGEAR_CONFIGURATION_PARAMETERS = configuration.THINKGEAR_CONFIGURATION_PARAMETERS

THINKGEAR_AUTHORIZATION_ENABLED = configuration.THINKGEAR_AUTHORIZATION_ENABLED
AUTHORIZATION_REQUEST = configuration.THINKGEAR_AUTHORIZATION_REQUEST

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_network_client_thinkgear:
	
	def __init__(self, log, \
		          server_host=SERVER_HOST, \
		          server_port=SERVER_PORT, \
		          DEBUG=DEBUG, \
		          parent=None):
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent=parent
		
		self.server_host = server_host
		self.server_port = server_port
		
		self.is_authorized = True
		
		self.configureNetwork()
	
	
	##################################################################
	
	def configureNetwork(self):
	
		#self.blockSize = 0
		self.socket = QtNetwork.QTcpSocket()
		self.socket.name = 'ThinkGear Client'
		
		self.socket.readyRead.connect(self.printReply)
		self.socket.error.connect(self.displayError)
		
		# Perform ThinkGear authorization if enabled
		if THINKGEAR_AUTHORIZATION_ENABLED:
			self.sendCommand(AUTHORIZATION_REQUEST)
			self.socket.waitForReadyRead()
			self.socket.disconnectFromHost()
		
		self.sendCommand(THINKGEAR_CONFIGURATION_PARAMETERS)
	
	
	##################################################################
	
	def printReply(self):
		
		socket_buffer = self.socket.readAll()
		
		for packet in socket_buffer.split(DELIMITER):
			
			if packet != '':
				
				try:
					
					data = json.loads(packet.data())
				
				
				except Exception, e:
					
					if self.DEBUG:
						print "ERROR [%s]: Exception parsing packet:" % self.socket.name,
						print packet.data()
						print "ERROR [%s]: Data packet" % self.socket.name,
						print e
					
					continue
				
				
				else:
					
					if self.DEBUG:
						print "--> [%s] Received:" % self.socket.name,
						print data
					
					self.processPacketThinkGear(data)
	
	
	##################################################################
	
	def displayError(self, socketError):
		
		if self.DEBUG:
			if ((socketError != QtNetwork.QAbstractSocket.RemoteHostClosedError) and \
				 (socketError != QtNetwork.QAbstractSocket.SocketTimeoutError)):
				print "ERROR [%s]:" % self.socket.name,
				print self.socket.errorString()
		
		
		if (self.parent != None):
		
			if ((socketError == QtNetwork.QAbstractSocket.RemoteHostClosedError) or \
				 (socketError != QtNetwork.QAbstractSocket.SocketTimeoutError)):
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
	
	def sendCommand(self, command):
		
		if self.DEBUG:
			print "<-- [%s] Sending:" % self.socket.name,
			print command
		
		self.socket.abort()
		self.socket.connectToHost(self.server_host, self.server_port)
		
		data = json.dumps(command)
		
		self.socket.waitForConnected(CLIENT_NO_REPLY_WAIT)
		
		self.socket.write(data)
		
		try:
			self.socket.waitForBytesWritten(CLIENT_NO_REPLY_WAIT)
		except Exception, e:
			print "ERROR [%s]: Exception:" % self.socket.name,
			print e
	
	
	##################################################################
	
	def processPacketThinkGear(self, packet):
		
		if ('isAuthorized' in packet.keys()):
			self.isAuthorized = packet['isAuthorized']
		
		# Pass GUI updating to Client Interface application
		if (self.parent != None):
			self.parent.processPacketThinkGear(packet)
		
	
	##################################################################
	
	def disconnectFromHost(self):
		
		self.socket.disconnectFromHost()


#####################################################################
# Command line class
#####################################################################

class puzzlebox_brainstorms_network_client_thinkgear_command_line( \
	      puzzlebox_brainstorms_network_client_thinkgear):
	
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
			command = None
		
		
		return(command)


#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_thinkgear')
	log = None
	
	command_parameters = sys.argv[1:]
	
	#log.info("Command parameters: %s" % command_parameters)
	
	app = QtCore.QCoreApplication(sys.argv)
	
	client = puzzlebox_brainstorms_network_client_thinkgear_command_line(log, \
	            command_parameters, \
	            server_host=SERVER_HOST, \
	            server_port=SERVER_PORT, \
	            DEBUG=DEBUG)
	
	#while True:
		#while client.socket.waitForReadyRead(CLIENT_NO_REPLY_WAIT):
			#pass
	
	sys.exit(app.exec_())

