#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Interface - Network
#
# Copyright Puzzlebox Productions, LLC (2010)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2010.10.01

"""

import os, sys

try:
	import PySide as PyQt4
	from PySide import QtGui
except:
	print "Using PyQt4 module"
	from PyQt4 import QtGui
else:
	print "Using PySide module"

#from PyQt4 import QtGui
#from PySide import QtGui


import Puzzlebox.Brainstorms.Interface as client_interface
#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

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
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_interface')
	log = None
	
	#for each in sys.argv:
		
		#if each.startswith("--host="):
			#server_host = each[ len("--host="): ]
		#if each.startswith("--port="):
			#server_port = each[ len("--port="): ]
	
	app = QtGui.QApplication(sys.argv)
	
	window = client_interface.puzzlebox_brainstorms_client_interface(log, DEBUG=DEBUG)
	window.show()
	
	sys.exit(app.exec_())


