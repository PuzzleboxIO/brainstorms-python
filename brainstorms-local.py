#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Interface - Local
#
# Copyright Puzzlebox Productions, LLC (2010-2011)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2011.04.14
"""

__doc__ = """|
Linux Examples:
#hcitool scan # Find devices
#sdptool search sp 00:16:53:09:12:0F # Examine serial services on device
#hciconfig hci0 sspmode 0 # ignore this step as device seems to work with sspmode enabled
rfcomm bind rfcomm1 00:16:53:09:12:0F 1 # bind /dev/rfcomm1 to channel 1 on device
rfcomm release 00:16:53:09:12:0F # disconnect device
"""

import os, sys
import signal

#if (sys.platform == 'win32'):
	#sys.path.append('C:\Python26\Lib\PyQt4\bin')

try:
	import PySide as PyQt4
	from PySide import QtCore, QtGui, QtNetwork
except:
	print "Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork
else:
	print "Using PySide module"


import Puzzlebox.Brainstorms.Configuration as configuration
import Puzzlebox.Brainstorms.Interface as client_interface
import Puzzlebox.Brainstorms.Client as brainstorms_client
import Puzzlebox.Brainstorms.Server as server
#import Puzzlebox.Brainstorms.NXT_Control as nxt_control
#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

SERVER_INTERFACE = configuration.BRAINSTORMS_SERVER_INTERFACE
SERVER_HOST = configuration.BRAINSTORMS_SERVER_HOST
SERVER_PORT = configuration.BRAINSTORMS_SERVER_PORT

CLIENT_NO_REPLY_WAIT = configuration.CLIENT_NO_REPLY_WAIT * 1000

DELIMITER = configuration.BRAINSTORMS_DELIMITER

BLUETOOTH_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

VARIABLE_CONTROL_DURATION = configuration.BRAINSTORMS_VARIABLE_CONTROL_DURATION

#####################################################################
# Classes
#####################################################################

#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	# Perform correct KeyboardInterrupt handling
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_interface')
	log = None
	
	# Collect default settings and command line parameters
	server_interface = SERVER_INTERFACE
	server_host = SERVER_HOST
	server_port = SERVER_PORT
	
	for each in sys.argv:
		
		if each.startswith("--interface="):
			server_interface = each[ len("--interface="): ]
		if each.startswith("--host="):
			server_host = each[ len("--host="): ]
		if each.startswith("--port="):
			server_port = each[ len("--port="): ]
	
	app = QtGui.QApplication(sys.argv)
	
	server = server.puzzlebox_brainstorms_network_server(log, \
	            server_interface, \
	            server_port, \
	            embedded_mode=True, \
	            robot_type=None, \
	            DEBUG=DEBUG)
	
	
	window = client_interface.puzzlebox_brainstorms_client_interface(log, \
	                                                                 server=server, \
	                                                                 DEBUG=DEBUG)
	
	if configuration.AUTOCONNECT_TO_NXT_DEVICE is True:
		window.connectToBrainstormsServer()
	
	window.show()
	
	sys.exit(app.exec_())

