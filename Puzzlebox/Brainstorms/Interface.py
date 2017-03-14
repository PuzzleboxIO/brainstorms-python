#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Interface
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2012.08.20

"""

__todo__ = """
 - ERROR: could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0' /dev/ttyUSB0
 - ERROR: Could not configure port: (5, 'Input/output error') /dev/ttyS0
 - server may not correctly handle multiple clients connected
      to an embedded Brainstorms server
 - add setting to configuration.ini for which helicopter command gets 
      called when speed reaches threshold
 - disable autorepeating on shortcut keys
 - update configuration.ini file with settings entered into interface

"""

import os, sys, time
import urllib

if (sys.platform == 'win32'):
	DEFAULT_IMAGE_PATH = 'images'
	import _winreg as winreg
	import itertools
	import re
	import serial
else:
	#import bluetooth
	if os.path.exists('/usr/share/puzzlebox_brainstorms'):
		os.chdir('/usr/share/puzzlebox_brainstorms')
	if os.path.exists('/usr/share/puzzlebox_brainstorms'):
		DEFAULT_IMAGE_PATH = '/usr/share/puzzlebox_brainstorms/images'
	else:
		DEFAULT_IMAGE_PATH = os.path.join( os.getcwd(), 'images')

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
		print "INFO: [Brainstorms:Interface] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:Interface] Using PyQt4 module"
	from PyQt4 import QtCore, QtGui, QtNetwork

from Interface_Design import Ui_Form as Design

import simplejson as json

import Client as brainstorms_client
import Puzzlebox.Brainstorms.ThinkGear.Client as thinkgear_client
import Helicopter_Control as helicopter_control
import Wheelchair_Control as wheelchair_control
#import puzzlebox_logger

#####################################################################
# Globals
#####################################################################

DEBUG = 1

BLINK_DETECTION_ENABLED = configuration.BLINK_DETECTION_ENABLED
BLINK_DETECTION_THRESHOLD = configuration.BLINK_DETECTION_THRESHOLD
BLINK_DETECTION_VALID_RANGE = configuration.BLINK_DETECTION_VALID_RANGE

BLINK_DETECTION_INCLUDE_FORWARD = configuration.BLINK_DETECTION_INCLUDE_FORWARD
BLINK_DETECTION_INCLUDE_LEFT = configuration.BLINK_DETECTION_INCLUDE_LEFT
BLINK_DETECTION_INCLUDE_RIGHT = configuration.BLINK_DETECTION_INCLUDE_RIGHT
BLINK_DETECTION_INCLUDE_REVERSE = configuration.BLINK_DETECTION_INCLUDE_REVERSE

THINKGEAR_POWER_THRESHOLDS = configuration.THINKGEAR_POWER_THRESHOLDS

DEFAULT_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

#NXT_BLUETOOTH_DEVICE = configuration.NXT_BLUETOOTH_DEVICE

DEFAULT_NXT_POWER_LEVEL = configuration.DEFAULT_NXT_POWER_LEVEL

WHEELCHAIR_CONTROL_EEG = configuration.WHEELCHAIR_CONTROL_EEG

THINKGEAR_SERVER_HOST = configuration.THINKGEAR_SERVER_HOST
THINKGEAR_SERVER_PORT = configuration.THINKGEAR_SERVER_PORT

BRAINSTORMS_FEEDBACK_URL = 'http://brainstorms.puzzlebox.info/contact_cgi.php'

DEVICE_PATH = '/dev'
PATH_TO_HCITOOL = '/usr/bin/hcitool'

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_client_interface(QtGui.QWidget, Design):
	
	def __init__(self, log, server=None, DEBUG=DEBUG, parent = None):
		
		self.log = log
		self.DEBUG = DEBUG
		
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		
		self.configureSettings()
		self.connectWidgets()
		
		self.name = "Brainstorms Interface"
		
		self.robot_type = None
		
		self.brainstormsServer = server
		self.brainstormsClient = None
		
		self.helicopter = None
		self.wheelchair = None
		
		self.drive_state = 'stop_motors'
		self.current_speed = 0
		
		self.current_helicopter_state = 'neutral'
		
		self.blinks = {}
	
	
	##################################################################
	
	def configureSettings(self):
		
		# Brainstorms Interface
		
		image_path = "puzzlebox.ico"
		if not os.path.exists(image_path):
			image_path = os.path.join(DEFAULT_IMAGE_PATH, image_path)
		
		if os.path.exists(image_path):
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(image_path), \
				            QtGui.QIcon.Normal, \
				            QtGui.QIcon.Off)
			self.setWindowIcon(icon)
		
		image_path = "puzzlebox_logo.png"
		if not os.path.exists(image_path):
			image_path = os.path.join(DEFAULT_IMAGE_PATH, image_path)
		if os.path.exists(image_path):
			self.labelPuzzlebox.setPixmap(QtGui.QPixmap(image_path))
		
		self.pushButtonTurnLeft.setEnabled(False)
		self.pushButtonForward.setEnabled(False)
		self.pushButtonTurnRight.setEnabled(False)
		self.pushButtonTurnLeftReverse.setEnabled(False)
		self.pushButtonReverse.setEnabled(False)
		self.pushButtonTurnRightReverse.setEnabled(False)
		
		self.pushButtonConcentrationEnable.setDown(True)
		self.pushButtonRelaxationEnable.setDown(True)
		self.pushButtonSpeedEnable.setDown(True)
		
		
		# Search for available Serial and Bluetooth devices
		self.searchForDevices()
		
		
		# Robotics
		self.textLabelRobotStatus.setText("Status: Disconnected")
		
		# Display communication port for LEGO Mindstorms NXT device
		#self.lineEditNXTPort.setText(DEFAULT_DEVICE)
		self.comboBoxRobotPortSelect.setEnabled(True)
		
		
		# RC Helicopter
		self.textLabelHelicopterStatus.setText("Status: Disconnected")
		
		
		# Wheelchair
		self.textLabelWheelchairStatus.setText("Status: Disconnected")
		
		
		# Control Panel
		
		# Display Host for ThinkGear Connect Socket Server
		self.lineEditThinkGearHost.setText(THINKGEAR_SERVER_HOST)
		#self.lineEditThinkGearHost.setEnabled(False)
		
		# Display Port for ThinkGear Connect Socket Server
		self.lineEditThinkGearPort.setText('%i' % THINKGEAR_SERVER_PORT)
		#self.lineEditThinkGearPort.setEnabled(False)
		
		
		self.lineEditLeftMotorPort.setText( \
		   configuration.NXT_MOTOR_PORT_LEFT.upper() )
		self.lineEditRightMotorPort.setText( \
		   configuration.NXT_MOTOR_PORT_RIGHT.upper() )
		self.checkBoxMotorSpinReversed.setChecked( \
		   configuration.NXT_MOTORS_MOUNTED_BACKWARDS)
		
		self.lineEditBlinkDetectionThreshold.setText( \
			"%s" % configuration.BLINK_DETECTION_THRESHOLD)
		self.checkBoxBlinkDetectionEnabled.setChecked( \
			configuration.BLINK_DETECTION_ENABLED)
	
	
	##################################################################
	
	def getMinimumThreshold(self, threshold):
		
		'''Return the minimum detection level which results
		in a non-zero power setting'''
		
		minimum = 100
		
		threshold_keys = threshold.keys()
		threshold_keys.sort()
		threshold_keys.reverse()
		
		for key in threshold_keys:
			
			if ((threshold[key] < minimum) and \
				 (threshold[key] > 0)):
				minimum = key
		
		
		return(minimum)
	
	
	##################################################################
	
	def configureNetworkBrainstorms(self):
		
		self.robot_type = str(self.comboBoxRobotTypeSelect.currentText())
		if self.robot_type == 'LEGO Mindstorms':
			self.robot_type = 'NXT'
		
		device_address = str(self.comboBoxRobotPortSelect.currentText())
		
		self.brainstormsClient = \
		   brainstorms_client.puzzlebox_brainstorms_network_client( \
			   self.log, \
			   device_address=device_address, \
			   robot_type=self.robot_type, \
			   parent=self)
		
		self.brainstormsClient.sendCommand('connect', \
		                                   device_address=device_address)
		
		if self.robot_type == 'NXT':
			self.updateLeftMotorPort()
			self.updateRightMotorPort()
			self.updateMotorSpinReversed()
	
	
	##################################################################
	
	def connectToBrainstormsServer(self):
		
		# Prevent attempting to connect to a device which does not exist
		device = str(self.comboBoxRobotPortSelect.currentText())
		if device == 'N/A':
			self.pushButtonRobotConnect.setChecked(False)
			return
		if (sys.platform != 'win32'):
			if ((not device.startswith(DEVICE_PATH)) or \
			    (not os.path.exists(device))):
				self.searchForDevices()
				self.pushButtonRobotConnect.setChecked(False)
				return
		
		
		if self.DEBUG:
			print "<---- [%s] Connecting to Brainstorms Server" % self.name
		
		self.configureNetworkBrainstorms()
		
		#if (self.brainstormsClient.socket.state() != QtNetwork.QAbstractSocket.ConnectedState):
			#QtGui.QMessageBox.information(self, \
					                        #self.brainstormsClient.socket.name, \
					   #"Failed to connect to Brainstorms socket server")
		
		#else:
		self.disconnect(self.pushButtonRobotConnect, \
							QtCore.SIGNAL("clicked()"), \
							self.connectToBrainstormsServer)
		
		self.connect(self.pushButtonRobotConnect, \
							QtCore.SIGNAL("clicked()"), \
							self.disconnectFromBrainstormsServer)
		
		self.textLabelRobotStatus.setText("Status: Connected")
		self.pushButtonRobotConnect.setText('Disconnect')
		
		self.comboBoxRobotTypeSelect.setEnabled(False)
		self.comboBoxRobotPortSelect.setEnabled(False)
		self.pushButtonRobotSearch.setEnabled(False)
		
		self.pushButtonTurnLeft.setEnabled(True)
		self.pushButtonForward.setEnabled(True)
		self.pushButtonTurnRight.setEnabled(True)
		self.pushButtonTurnLeftReverse.setEnabled(True)
		self.pushButtonReverse.setEnabled(True)
		self.pushButtonTurnRightReverse.setEnabled(True)
		
		self.pushButtonTurnLeft.setFlat(True)
		self.pushButtonForward.setFlat(False)
		self.pushButtonTurnRight.setFlat(True)
		self.pushButtonTurnLeftReverse.setFlat(True)
		self.pushButtonReverse.setFlat(True)
		self.pushButtonTurnRightReverse.setFlat(True)
		
		
		self.pushButtonNXTMessageOne.setEnabled(True)
		self.pushButtonNXTMessageTwo.setEnabled(True)
		self.pushButtonNXTMessageThree.setEnabled(True)
		self.pushButtonNXTMessageFour.setEnabled(True)
		#self.pushButtonNXTMessageFive.setEnabled(True)
		#self.pushButtonNXTMessageSix.setEnabled(True)
		
		self.pushButtonConcentrationEnable.setEnabled(True)
		self.pushButtonRelaxationEnable.setEnabled(True)
		self.pushButtonSpeedEnable.setEnabled(True)
		
		self.pushButtonMessageOne.setEnabled(True)
		self.pushButtonMessageTwo.setEnabled(True)
		self.pushButtonMessageThree.setEnabled(True)
		self.pushButtonMessageFour.setEnabled(True)
		#self.pushButtonMessageFive.setEnabled(True)
		#self.pushButtonMessageSix.setEnabled(True)
	
	
	##################################################################
	
	def disconnectFromBrainstormsServer(self):
		
		if self.DEBUG:
			print "- - [%s] Disconnecting from Brainstorms Server" % self.name
		
		self.stopMotors()
		
		# Ensure the stopMotors command has been received by the server
		# so the NXT robot will stop before the client disconnects
		self.brainstormsClient.socket.flush()
		
		self.brainstormsClient.socket.disconnectFromHost()
		
		self.disconnect(self.pushButtonRobotConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromBrainstormsServer)
		
		self.connect(self.pushButtonRobotConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToBrainstormsServer)
		
		self.textLabelRobotStatus.setText("Status: Disconnected")
		self.pushButtonRobotConnect.setText('Connect')
		
		self.comboBoxRobotTypeSelect.setEnabled(True)
		self.comboBoxRobotPortSelect.setEnabled(True)
		self.pushButtonRobotSearch.setEnabled(True)
		
		self.pushButtonTurnLeft.setEnabled(False)
		self.pushButtonForward.setEnabled(False)
		self.pushButtonTurnRight.setEnabled(False)
		self.pushButtonTurnLeftReverse.setEnabled(False)
		self.pushButtonReverse.setEnabled(False)
		self.pushButtonTurnRightReverse.setEnabled(False)
		
		self.pushButtonTurnLeft.setFlat(False)
		self.pushButtonForward.setFlat(False)
		self.pushButtonTurnRight.setFlat(False)
		self.pushButtonTurnLeftReverse.setFlat(False)
		self.pushButtonReverse.setFlat(False)
		self.pushButtonTurnRightReverse.setFlat(False)
		
		self.pushButtonNXTMessageOne.setEnabled(False)
		self.pushButtonNXTMessageTwo.setEnabled(False)
		self.pushButtonNXTMessageThree.setEnabled(False)
		self.pushButtonNXTMessageFour.setEnabled(False)
		#self.pushButtonNXTMessageFive.setEnabled(False)
		#self.pushButtonNXTMessageSix.setEnabled(False)
		
		self.pushButtonConcentrationEnable.setEnabled(False)
		self.pushButtonRelaxationEnable.setEnabled(False)
		self.pushButtonSpeedEnable.setEnabled(False)
		
		self.pushButtonMessageOne.setEnabled(False)
		self.pushButtonMessageTwo.setEnabled(False)
		self.pushButtonMessageThree.setEnabled(False)
		self.pushButtonMessageFour.setEnabled(False)
		#self.pushButtonMessageFive.setEnabled(False)
		#self.pushButtonMessageSix.setEnabled(False)
		
		self.brainstormsClient = None
		
		self.searchForDevices()
	
	
	##################################################################
	
	def connectToThinkGearHost(self):
		
		if self.DEBUG:
			print "Connecting to ThinkGear Host"
		
		server_host = str(self.lineEditThinkGearHost.text())
		server_port = int(self.lineEditThinkGearPort.text())
		
		self.thinkgearClient = \
		   thinkgear_client.puzzlebox_brainstorms_network_client_thinkgear( \
			   self.log, \
			   server_host=server_host, \
			   server_port=server_port, \
			   DEBUG=0, \
			   parent=self)
		
		if (self.thinkgearClient.socket.state() != QtNetwork.QAbstractSocket.ConnectedState):
			QtGui.QMessageBox.information(self, \
					                        self.thinkgearClient.socket.name, \
					   "Failed to connect to ThinkGear socket server")
		
		else:
			self.disconnect(self.pushButtonThinkGearConnect, \
							 QtCore.SIGNAL("clicked()"), \
							 self.connectToThinkGearHost)
			
			self.connect(self.pushButtonThinkGearConnect, \
							 QtCore.SIGNAL("clicked()"), \
							 self.disconnectFromThinkGearHost)
			
			self.pushButtonThinkGearConnect.setText('Disconnect')
			
			self.comboBoxEEGHeadsetModel.setEnabled(False)
			self.comboBoxEEGSource.setEnabled(False)
			self.lineEditThinkGearHost.setEnabled(False)
			self.lineEditThinkGearPort.setEnabled(False)
			
			self.progressBarBlinkDetection.setValue(0)
	
	
	##################################################################
	
	def disconnectFromThinkGearHost(self):
		
		if self.DEBUG:
			print "Disconnecting from ThinkGear Host"
		
		self.thinkgearClient.disconnectFromHost()
		
		self.disconnect(self.pushButtonThinkGearConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromThinkGearHost)
		
		self.connect(self.pushButtonThinkGearConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToThinkGearHost)
		
		self.pushButtonTurnLeft.emit(QtCore.SIGNAL("released()"))
		self.pushButtonForward.emit(QtCore.SIGNAL("released()"))
		self.pushButtonTurnRight.emit(QtCore.SIGNAL("released()"))
		self.pushButtonTurnLeftReverse.emit(QtCore.SIGNAL("released()"))
		self.pushButtonReverse.emit(QtCore.SIGNAL("released()"))
		self.pushButtonTurnRightReverse.emit(QtCore.SIGNAL("released()"))
		
		self.pushButtonThinkGearConnect.setText('Connect')
		
		self.comboBoxEEGHeadsetModel.setEnabled(True)
		self.comboBoxEEGSource.setEnabled(True)
		self.lineEditThinkGearHost.setEnabled(True)
		self.lineEditThinkGearPort.setEnabled(True)
		
		self.progressBarConcentration.setValue(0)
		self.progressBarRelaxation.setValue(0)
		self.progressBarSpeed.setValue(0)
	
		self.progressBarHelicopterConcentration.setValue(0)
		self.progressBarHelicopterRelaxation.setValue(0)
		self.progressBarHelicopterSpeed.setValue(0)
	
		self.progressBarWheelchairConcentration.setValue(0)
		self.progressBarWheelchairRelaxation.setValue(0)
		self.progressBarWheelchairSpeed.setValue(0)
	
	
	##################################################################
	
	def connectToRCHelicopter(self):

		# Prevent attempting to connect to a device which does not exist
		device = str(self.comboBoxHelicopterPortSelect.currentText())
		if device == 'N/A':
			self.pushButtonHelicopterConnect.setChecked(False)
			return
		if (sys.platform != 'win32'):
			if ((not device.startswith(DEVICE_PATH)) or \
			    (not os.path.exists(device))):
				self.searchForDevices()
				self.pushButtonHelicopterConnect.setChecked(False)
				return

		self.helicopter = \
		   helicopter_control.puzzlebox_brainstorms_helicopter_control( \
		      device_address=device,
		      command='neutral', \
		      DEBUG=self.DEBUG)
		
		self.helicopter.start()
		
		self.disconnect(self.pushButtonHelicopterConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToRCHelicopter)
		
		self.connect(self.pushButtonHelicopterConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromRCHelicopter)
		
		self.pushButtonHelicopterConnect.setText('Disconnect')
		
		self.comboBoxHelicopterTransmitter.setEnabled(False)
		self.comboBoxHelicopterPortSelect.setEnabled(False)
		self.pushButtonHelicopterSearch.setEnabled(False)
		
		self.pushButtonHelicopterHover.setEnabled(True)
		self.pushButtonHelicopterFlyForward.setEnabled(True)
		self.pushButtonHelicopterLand.setEnabled(True)
		self.pushButtonHelicopterThrottle.setEnabled(True)
		self.verticalSliderHelicopterThrottle.setEnabled(True)
		self.pushButtonHelicopterElevatorForward.setEnabled(True)
		self.verticalSliderHelicopterElevatorForward.setEnabled(True)
		self.pushButtonHelicopterElevatorReverse.setEnabled(True)
		self.verticalSliderHelicopterElevatorReverse.setEnabled(True)
		self.pushButtonHelicopterRudderLeft.setEnabled(True)
		self.horizontalSliderHelicopterRudderLeft.setEnabled(True)
		self.pushButtonHelicopterRudderRight.setEnabled(True)
		self.horizontalSliderHelicopterRudderRight.setEnabled(True)
		self.pushButtonHelicopterAileronLeft.setEnabled(True)
		self.horizontalSliderHelicopterAileronLeft.setEnabled(True)
		self.pushButtonHelicopterAileronRight.setEnabled(True)
		self.horizontalSliderHelicopterAileronRight.setEnabled(True)
		
		self.pushButtonHelicopterConcentrationEnable.setEnabled(True)
		self.pushButtonHelicopterRelaxationEnable.setEnabled(True)
		self.pushButtonHelicopterSpeedEnable.setEnabled(True)
	
	
	##################################################################
	
	def disconnectFromRCHelicopter(self):
		
		self.helicopter.neutral()
		self.current_helicopter_state = 'neutral'
		
		self.helicopter.stop()
		
		self.disconnect(self.pushButtonHelicopterConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromRCHelicopter)
		
		self.connect(self.pushButtonHelicopterConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToRCHelicopter)
		
		self.pushButtonHelicopterConnect.setText('Connect')
		
		self.comboBoxHelicopterTransmitter.setEnabled(True)
		self.comboBoxHelicopterPortSelect.setEnabled(True)
		self.pushButtonHelicopterSearch.setEnabled(True)
		
		self.pushButtonHelicopterHover.setEnabled(False)
		self.pushButtonHelicopterFlyForward.setEnabled(False)
		self.pushButtonHelicopterLand.setEnabled(False)
		self.pushButtonHelicopterThrottle.setEnabled(False)
		self.verticalSliderHelicopterThrottle.setEnabled(False)
		self.pushButtonHelicopterElevatorForward.setEnabled(False)
		self.verticalSliderHelicopterElevatorForward.setEnabled(False)
		self.pushButtonHelicopterElevatorReverse.setEnabled(False)
		self.verticalSliderHelicopterElevatorReverse.setEnabled(False)
		self.pushButtonHelicopterRudderLeft.setEnabled(False)
		self.horizontalSliderHelicopterRudderLeft.setEnabled(False)
		self.pushButtonHelicopterRudderRight.setEnabled(False)
		self.horizontalSliderHelicopterRudderRight.setEnabled(False)
		self.pushButtonHelicopterAileronLeft.setEnabled(False)
		self.horizontalSliderHelicopterAileronLeft.setEnabled(False)
		self.pushButtonHelicopterAileronRight.setEnabled(False)
		self.horizontalSliderHelicopterAileronRight.setEnabled(False)
		
		self.pushButtonHelicopterConcentrationEnable.setEnabled(False)
		self.pushButtonHelicopterRelaxationEnable.setEnabled(False)
		self.pushButtonHelicopterSpeedEnable.setEnabled(False)
	
	
	##################################################################
	
	def connectToWheelchair(self):
		
		# Prevent attempting to connect to a device which does not exist
		device = str(self.comboBoxWheelchairPortSelect.currentText())
		if device == 'N/A':
			self.pushButtonWheelchairConnect.setChecked(False)	
			return
		if (sys.platform != 'win32'):
			if ((not device.startswith(DEVICE_PATH)) or \
			    (not os.path.exists(device))):
				self.searchForDevices()
				self.pushButtonWheelchairConnect.setChecked(False)
				return
		
		self.wheelchair = \
		   wheelchair_control.puzzlebox_brainstorms_wheelchair_control( \
		      device_address=device,
		      command='gui', \
		      DEBUG=self.DEBUG)
		
		self.wheelchair.start()
		
		self.disconnect(self.pushButtonWheelchairConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToWheelchair)
		
		self.connect(self.pushButtonWheelchairConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromWheelchair)
		
		self.pushButtonWheelchairConnect.setText('Disconnect')
		
		self.comboBoxWheelchairTransmitter.setEnabled(False)
		self.comboBoxWheelchairPortSelect.setEnabled(False)
		self.pushButtonWheelchairSearch.setEnabled(False)
		
		self.pushButtonWheelchairForward.setEnabled(True)
		self.pushButtonWheelchairReverse.setEnabled(True)
		self.pushButtonWheelchairLeft.setEnabled(True)
		self.pushButtonWheelchairRight.setEnabled(True)
		self.pushButtonWheelchairStop.setEnabled(True)
		self.dialWheelchairSpeed.setEnabled(True)
		
		self.pushButtonWheelchairConcentrationEnable.setEnabled(True)
		self.pushButtonWheelchairRelaxationEnable.setEnabled(True)
		self.pushButtonWheelchairSpeedEnable.setEnabled(True)
		
		# Safety Measure: Explicitely require wheelchair speed control
		# to be enabled each time it wheelchair is connected
		self.pushButtonWheelchairSpeedEnable.setChecked(False)
		self.pushButtonWheelchairSpeedEnable.setText('Disabled')
		self.progressBarWheelchairSpeed.setValue(0)
	
	
	##################################################################
	
	def disconnectFromWheelchair(self):
		
		#self.stopWheelchair()
		
		self.wheelchair.stop()
		
		self.disconnect(self.pushButtonWheelchairConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disconnectFromWheelchair)
		
		self.connect(self.pushButtonWheelchairConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToWheelchair)
		
		self.pushButtonWheelchairConnect.setText('Connect')
		
		self.comboBoxWheelchairTransmitter.setEnabled(True)
		self.comboBoxWheelchairPortSelect.setEnabled(True)
		self.pushButtonWheelchairSearch.setEnabled(True)
		
		self.pushButtonWheelchairForward.setEnabled(False)
		self.pushButtonWheelchairReverse.setEnabled(False)
		self.pushButtonWheelchairLeft.setEnabled(False)
		self.pushButtonWheelchairRight.setEnabled(False)
		self.pushButtonWheelchairStop.setEnabled(False)
		self.dialWheelchairSpeed.setEnabled(False)
		
		self.pushButtonWheelchairConcentrationEnable.setEnabled(False)
		self.pushButtonWheelchairRelaxationEnable.setEnabled(False)
		self.pushButtonWheelchairSpeedEnable.setEnabled(False)
		
		# Safety Measure: Explicitely require wheelchair speed control
		# to be enabled each time it wheelchair is connected
		self.pushButtonWheelchairSpeedEnable.setChecked(False)
		self.pushButtonWheelchairSpeedEnable.setText('Disabled')
		self.progressBarWheelchairSpeed.setValue(0)
	
	
	##################################################################
	
	def updateConcentrationButton(self):
		
		if self.pushButtonConcentrationEnable.isChecked():
			
			self.pushButtonConcentrationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonConcentrationEnable.setText('Disabled')
			self.progressBarConcentration.setValue(0)
		
		
		self.updateRobotSpeed()
	
	
	##################################################################
	
	def updateRelaxationButton(self):
		
		if self.pushButtonRelaxationEnable.isChecked():
		
			self.pushButtonRelaxationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonRelaxationEnable.setText('Disabled')
			self.progressBarRelaxation.setValue(0)
		
		
		self.updateRobotSpeed()
	
	
	##################################################################
	
	def updateSpeedButton(self):
		
		if self.pushButtonSpeedEnable.isChecked():
		
			self.pushButtonSpeedEnable.setText('Enabled')
			self.updateRobotSpeed()
		
		else:
			
			self.pushButtonSpeedEnable.setText('Disabled')
			self.progressBarSpeed.setValue(0)
			self.stopMotors()
	
	
	##################################################################
	
	def updateHelicopterConcentrationButton(self):
		
		if self.pushButtonHelicopterConcentrationEnable.isChecked():
			
			self.pushButtonHelicopterConcentrationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonHelicopterConcentrationEnable.setText('Disabled')
			self.progressBarHelicopterConcentration.setValue(0)
		
		
		self.updateHelicopterSpeed()
	
	
	##################################################################
	
	def updateHelicopterRelaxationButton(self):
		
		if self.pushButtonHelicopterRelaxationEnable.isChecked():
		
			self.pushButtonHelicopterRelaxationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonHelicopterRelaxationEnable.setText('Disabled')
			self.progressBarHelicopterRelaxation.setValue(0)
		
		
		self.updateHelicopterSpeed()
	
	
	##################################################################
	
	def updateHelicopterSpeedButton(self):
		
		if self.pushButtonHelicopterSpeedEnable.isChecked():
		
			self.pushButtonHelicopterSpeedEnable.setText('Enabled')
			self.updateHelicopterSpeed()
		
		else:
			
			self.pushButtonHelicopterSpeedEnable.setText('Disabled')
			self.progressBarHelicopterSpeed.setValue(0)
			self.landHelicopter()
	
	
	##################################################################
	
	def updateWheelchairConcentrationButton(self):
		
		if self.pushButtonWheelchairConcentrationEnable.isChecked():
			
			self.pushButtonWheelchairConcentrationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonWheelchairConcentrationEnable.setText('Disabled')
			self.progressBarWheelchairConcentration.setValue(0)
		
		
		self.updateWheelchairSpeed()
	
	
	##################################################################
	
	def updateWheelchairRelaxationButton(self):
		
		if self.pushButtonWheelchairRelaxationEnable.isChecked():
		
			self.pushButtonWheelchairRelaxationEnable.setText('Enabled')
		
		else:
			
			self.pushButtonWheelchairRelaxationEnable.setText('Disabled')
			self.progressBarWheelchairRelaxation.setValue(0)
		
		
		self.updateWheelchairSpeed()
	
	
	##################################################################
	
	def updateWheelchairSpeedButton(self):
		
		if self.pushButtonWheelchairSpeedEnable.isChecked():
		
			self.pushButtonWheelchairSpeedEnable.setText('Enabled')
			self.updateWheelchairSpeed()
		
		else:
			
			self.pushButtonWheelchairSpeedEnable.setText('Disabled')
			self.progressBarWheelchairSpeed.setValue(0)
			self.stopWheelchair()
	
	
	##################################################################
	
	def connectWidgets(self):
		
		# LEGO Mindstorms Buttons
		self.connect(self.pushButtonTurnLeft, QtCore.SIGNAL("pressed()"), \
		             self.turnLeft)
		self.connect(self.pushButtonTurnLeft, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		self.connect(self.pushButtonForward, QtCore.SIGNAL("pressed()"), \
		             self.driveForward)
		self.connect(self.pushButtonForward, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		self.connect(self.pushButtonTurnRight, QtCore.SIGNAL("pressed()"), \
		             self.turnRight)
		self.connect(self.pushButtonTurnRight, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		self.connect(self.pushButtonTurnLeftReverse, QtCore.SIGNAL("pressed()"), \
		             self.turnLeftInReverse)
		self.connect(self.pushButtonTurnLeftReverse, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		self.connect(self.pushButtonReverse, QtCore.SIGNAL("pressed()"), \
		             self.driveReverse)
		self.connect(self.pushButtonReverse, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		self.connect(self.pushButtonTurnRightReverse, QtCore.SIGNAL("pressed()"), \
		             self.turnRightInReverse)
		self.connect(self.pushButtonTurnRightReverse, QtCore.SIGNAL("released()"), \
		             self.stopMotors)
		
		
		self.connect(self.pushButtonRobotSearch, \
			          QtCore.SIGNAL("clicked()"), \
			          self.searchForDevices)
		
		self.connect(self.pushButtonRobotConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToBrainstormsServer)
		
		
		self.connect(self.pushButtonConcentrationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateConcentrationButton)
		
		self.connect(self.pushButtonRelaxationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateRelaxationButton)
		
		self.connect(self.pushButtonSpeedEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateSpeedButton)
		
		
		self.connect(self.pushButtonNXTMessageOne, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageOne)
		
		self.connect(self.pushButtonNXTMessageTwo, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageTwo)
		
		self.connect(self.pushButtonNXTMessageThree, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageThree)
		
		self.connect(self.pushButtonNXTMessageFour, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageFour)
		
		#self.connect(self.pushButtonNXTMessageFive, QtCore.SIGNAL("pressed()"), \
		             #self.sendMessageFive)
		
		#self.connect(self.pushButtonNXTMessageSix, QtCore.SIGNAL("pressed()"), \
		             #self.sendMessageSix)
		
		
		
		# RC Helicopter Buttons
		self.connect(self.pushButtonHelicopterSearch, \
			          QtCore.SIGNAL("clicked()"), \
			          self.searchForDevices)
		
		self.connect(self.pushButtonHelicopterConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToRCHelicopter)
		
		
		self.connect(self.pushButtonHelicopterConcentrationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateHelicopterConcentrationButton)
		
		self.connect(self.pushButtonHelicopterRelaxationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateHelicopterRelaxationButton)
		
		self.connect(self.pushButtonHelicopterSpeedEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateHelicopterSpeedButton)
		
		
		self.connect(self.pushButtonHelicopterHover, \
			          QtCore.SIGNAL("clicked()"), \
			          self.enableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterFlyForward, \
			          QtCore.SIGNAL("clicked()"), \
			          self.enableHelicopterFlyForward)
		
		self.connect(self.pushButtonHelicopterLand, \
			          QtCore.SIGNAL("clicked()"), \
			          self.landHelicopter)
		
		
		
		# Wheelchair Buttons
		self.connect(self.pushButtonWheelchairSearch, \
			          QtCore.SIGNAL("clicked()"), \
			          self.searchForDevices)
		
		self.connect(self.pushButtonWheelchairConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToWheelchair)
		
		
		self.connect(self.pushButtonWheelchairConcentrationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateWheelchairConcentrationButton)
		
		self.connect(self.pushButtonWheelchairRelaxationEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateWheelchairRelaxationButton)
		
		self.connect(self.pushButtonWheelchairSpeedEnable, \
			          QtCore.SIGNAL("clicked()"), \
			          self.updateWheelchairSpeedButton)
		
		
		self.connect(self.pushButtonWheelchairForward, \
			          QtCore.SIGNAL("pressed()"), \
			          self.driveWheelchairForward)
		self.connect(self.pushButtonWheelchairReverse, \
			          QtCore.SIGNAL("pressed()"), \
			          self.driveWheelchairReverse)
		self.connect(self.pushButtonWheelchairLeft, \
			          QtCore.SIGNAL("pressed()"), \
			          self.driveWheelchairLeft)
		self.connect(self.pushButtonWheelchairRight, \
			          QtCore.SIGNAL("pressed()"), \
			          self.driveWheelchairRight)

		if not WHEELCHAIR_CONTROL_EEG:
			# Manual control for Wheelchair
			# Allow drive instructions to be sent once (or repeatedly)
			self.connect(self.pushButtonWheelchairForward, \
				     QtCore.SIGNAL("released()"), \
				     self.stopWheelchair)		
			self.connect(self.pushButtonWheelchairReverse, \
				     QtCore.SIGNAL("released()"), \
				     self.stopWheelchair)
			self.connect(self.pushButtonWheelchairLeft, \
				     QtCore.SIGNAL("released()"), \
				     self.stopWheelchair)
			self.connect(self.pushButtonWheelchairRight, \
				     QtCore.SIGNAL("released()"), \
				     self.stopWheelchair)
		
		self.connect(self.pushButtonWheelchairStop, \
			          QtCore.SIGNAL("pressed()"), \
			          self.stopWheelchair)
		
		self.connect(self.dialWheelchairSpeed, \
		             QtCore.SIGNAL("valueChanged(int)"), \
		             self.updateWheelchairSpeed)
		
		
		
		# Control Panel Buttons
		self.connect(self.lineEditLeftMotorPort, QtCore.SIGNAL("textEdited(const QString &)"), \
		             self.updateLeftMotorPort)
		             
		self.connect(self.lineEditRightMotorPort, QtCore.SIGNAL("textEdited(const QString &)"), \
		             self.updateRightMotorPort)
		
		self.connect(self.checkBoxMotorSpinReversed, QtCore.SIGNAL("stateChanged(int)"), \
		             self.updateMotorSpinReversed)
		
		
		self.connect(self.pushButtonMessageOne, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageOne)
		
		self.connect(self.pushButtonMessageTwo, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageTwo)
		
		self.connect(self.pushButtonMessageThree, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageThree)
		
		self.connect(self.pushButtonMessageFour, QtCore.SIGNAL("pressed()"), \
		             self.sendMessageFour)
		
		#self.connect(self.pushButtonMessageFive, QtCore.SIGNAL("pressed()"), \
		             #self.sendMessageFive)
		
		#self.connect(self.pushButtonMessageSix, QtCore.SIGNAL("pressed()"), \
		             #self.sendMessageSix)
		
		
		self.connect(self.pushButtonThinkGearConnect, \
			          QtCore.SIGNAL("clicked()"), \
			          self.connectToThinkGearHost)
		
		self.connect(self.pushButtonSendFeedback, \
			          QtCore.SIGNAL("clicked()"), \
			          self.sendFeedback)
		
		
		#shortcut = QtGui.QShortcut(self)
		#shortcut.setKey(tr("Down"))
		#self.connect(shortcut, QtCore.SIGNAL("pressed()"), self.driveReverse)
		
		
		# Global Buttons
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Tab"))
		self.connect(action, QtCore.SIGNAL("triggered()"), self.rotateControlButtons)
		self.addAction(action)
		
		
		# Robot Buttons
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("W"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonForward, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Up"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonForward, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Left"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnLeft, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("A"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnLeft, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("S"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Down"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("D"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnRight, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Right"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnRight, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Z"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnLeftReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("C"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonTurnRightReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		
		# RC Helicopter Buttons
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Home"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterHover, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("["))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterHover, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("PgUp"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterFlyForward, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("]"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterFlyForward, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("End"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterLand, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("\\"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonHelicopterLand, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		
		# Wheelchair Buttons
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("i"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairForward, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("k"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("m"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairReverse, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("j"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairLeft, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("l"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairRight, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("Space"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonWheelchairStop, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		
		
		# Control Panel Buttons
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("1"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageOne, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("2"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageTwo, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("3"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageThree, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		action = QtGui.QAction(self)
		action.setShortcut(QtGui.QKeySequence("4"))
		self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageFour, QtCore.SLOT("animateClick()"))
		self.addAction(action)
		
		#action = QtGui.QAction(self)
		#action.setShortcut(QtGui.QKeySequence("5"))
		#self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageFive, QtCore.SLOT("animateClick()"))
		#self.addAction(action)
		
		#action = QtGui.QAction(self)
		#action.setShortcut(QtGui.QKeySequence("6"))
		#self.connect(action, QtCore.SIGNAL("activated()"), self.pushButtonNXTMessageSix, QtCore.SLOT("animateClick()"))
		#self.addAction(action)
		
		
		#self.pushButtonForward.setAutoRepeat(False)
		#self.pushButtonForward.setAutoRepeatDelay(0)
		#self.pushButtonForward.setAutoRepeatInterval(0)
	
	
	##################################################################
	
	def searchForDevices(self):
		
		nxt_devices = []
		rc_helicopter_devices = []
		wheelchair_devices = []
		
		#if (sys.platform != 'win32'):
		if False: # temporarily disabled
			
			# Bluetooth module doesn't compile properly under Windows
			
			bluetooth_devices = []
			
			try:
				bluetooth_devices = bluetooth.discover_devices( \
				                       duration=5, \
				                       flush_cache=True, \
				                       lookup_names=False)
			except:
				#command = '%s con' % PATH_TO_HCITOOL
				command = '%s scan' % PATH_TO_HCITOOL
				
				output = os.popen(command, 'r')
				
				for line in output.readlines():
					print line
					try:
						address = line.split(' ')[2]
					except:
						pass
					else:
						bluetooth_devices.append(address)
			
			for address in bluetooth_devices:
				device_name = bluetooth.lookup_name(address)
				if ((device_name == 'NXT') and \
				    (address not in nxt_devices)):
					nxt_devices.append(address)
			
			
			if self.DEBUG:
				print "Bluetooth NXT devices found:",
				print nxt_devices
		
		
		# List all serial devices
		serial_devices = self.enumerateSerialPorts()
		
		for serial_device in serial_devices:
			#serial_device = self.fullPortName(serial_device)
			nxt_devices.append(serial_device)
			rc_helicopter_devices.append(serial_device)
			wheelchair_devices.append(serial_device)
		
		
		# Configure combo boxes
		if nxt_devices == []:
			nxt_devices.append('N/A')
		
		if rc_helicopter_devices == []:
			rc_helicopter_devices.append('N/A')
		
		if wheelchair_devices == []:
			wheelchair_devices.append('N/A')
		
		
		# Don't reset combo boxes if already connected
		if self.pushButtonRobotConnect.text != 'Disconnect':
			
			self.comboBoxRobotPortSelect.clear()
			
			#nxt_devices.reverse()
			for nxt_device in nxt_devices:
				self.comboBoxRobotPortSelect.addItem(nxt_device)
		
		
		if self.pushButtonHelicopterConnect.text != 'Disconnect':
			
			self.comboBoxHelicopterPortSelect.clear()
			
			#rc_helicopter_devices.reverse()
			for rc_helicopter in rc_helicopter_devices:
				self.comboBoxHelicopterPortSelect.addItem(rc_helicopter)
		
		
		if self.pushButtonWheelchairConnect.text != 'Disconnect':
			
			self.comboBoxWheelchairPortSelect.clear()
			
			#rc_helicopter_devices.reverse()
			for wheelchair in wheelchair_devices:
				self.comboBoxWheelchairPortSelect.addItem(wheelchair)
	
	
	##################################################################
	
	def enumerateSerialPorts(self):
		
		""" Uses the Win32 registry to return an
		iterator of serial (COM) ports
		existing on this computer.
		
		from http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/
		"""
		
		serial_ports = []
		
		if (sys.platform == 'win32'):
			
			path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
			try:
				key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
			except WindowsError:
				#raise IterationError
				return []
				#pass
			
			for i in itertools.count():
				try:
					val = winreg.EnumValue(key, i)
					#yield str(val[1])
					serial_ports.append( str(val[1]) )
				except EnvironmentError:
					break
		
		
		else:
			
			if os.path.exists(DEVICE_PATH):
				device_list = os.listdir(DEVICE_PATH)
				
				device_list.sort()
			
				for device in device_list:
					if device.startswith('arduino'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('ttyUSB'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('rfcomm'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('ttyACM'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('ttyS'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('rfcomm'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('ttys0'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('tty.usbserial-FTF3NM1G'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('tty.usbserial'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				for device in device_list:
					if device.startswith('tty.NXT-DevB'):
						serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('tty.MindWaveMobile'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('tty.MindWave'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('tty.MindSet'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
				#for device in device_list:
					#if device.startswith('arduino'):
						#serial_ports.append( DEVICE_PATH + '/' + device )
		
		
		return(serial_ports)
	
	
	##################################################################
	
	def fullPortName(self, portname):
		
		""" Given a port-name (of the form COM7,
		COM12, CNCA0, etc.) returns a full
		name suitable for opening with the
		Serial class.
		"""
		
		m = re.match('^COM(\d+)$', portname)
		if m and int(m.group(1)) < 10:
			return portname
		
		return '\\\\.\\' + portname
	
	
	##################################################################
	
	# LEGO Mindstorms Controls
	
	def turnLeft(self):
		self.brainstormsClient.sendCommand('turn_left')
		self.drive_state = 'turn_left'
	
	def driveForward(self):
		#if self.DEBUG:
			#print "driveForward"
		#self.pushButtonForward.setDown(True)
		#if (self.drive_state != 'drive_forward'):
			#self.updateRobotSpeed(new_speed=DEFAULT_NXT_POWER_LEVEL)
		power = self.current_speed
		if power == 0:
			power=DEFAULT_NXT_POWER_LEVEL
		self.brainstormsClient.sendCommand('drive_forward', power=power)
		self.drive_state = 'drive_forward'
	
	def turnRight(self):
		self.brainstormsClient.sendCommand('turn_right')
		self.drive_state = 'turn_right'
	
	def turnLeftInReverse(self):
		self.brainstormsClient.sendCommand('turn_left_in_reverse')
		self.drive_state = 'turn_left_in_reverse'
	
	def driveReverse(self):
		self.brainstormsClient.sendCommand('drive_reverse')
		self.drive_state = 'drive_reverse'
	
	def turnRightInReverse(self):
		self.brainstormsClient.sendCommand('turn_right_in_reverse')
		self.drive_state = 'turn_right_in_reverse'
	
	def stopMotors(self):
		self.pushButtonTurnLeft.setDown(False)
		self.pushButtonForward.setDown(False)
		self.pushButtonTurnRight.setDown(False)
		self.pushButtonTurnLeftReverse.setDown(False)
		self.pushButtonReverse.setDown(False)
		self.pushButtonTurnRightReverse.setDown(False)
		if (self.current_speed != 0):
			self.updateRobotSpeed(new_speed=0)
		if self.brainstormsClient != None:
			self.brainstormsClient.sendCommand('stop_motors')
		self.drive_state = 'stop_motors'
	
	def sendMessageOne(self):
		message = str(self.lineEditMessageOne.text())
		self.brainstormsClient.sendCommand('send_message_1')
	
	def sendMessageTwo(self):
		message = str(self.lineEditMessageTwo.text())
		self.brainstormsClient.sendCommand('send_message_2')
	
	def sendMessageThree(self):
		message = str(self.lineEditMessageThree.text())
		self.brainstormsClient.sendCommand('send_message_3')
	
	def sendMessageFour(self):
		message = str(self.lineEditMessageFour.text())
		self.brainstormsClient.sendCommand('send_message_4')
	
	#def sendMessageFive(self):
		#message = str(self.lineEditMessageFive.text())
		#self.brainstormsClient.sendCommand('send_message_5')
	
	#def sendMessageSix(self):
		#message = str(self.lineEditMessageSix.text())
		#self.brainstormsClient.sendCommand('send_message_6')
	
	
	##################################################################
	
	def updateLeftMotorPort(self):
		
		motor_port = str(self.lineEditLeftMotorPort.text())
		motor_port = motor_port.lower()
		
		#print
		#print "new left motor port:",
		#print motor_port
		#print
		
		if (self.brainstormsClient != None):
			
			update = {'motor_port_left': motor_port}
			
			self.brainstormsClient.sendCommand('update', default_data=update)
	
	
	##################################################################
	
	def updateRightMotorPort(self):
		
		motor_port = str(self.lineEditRightMotorPort.text())
		motor_port = motor_port.lower()
		
		#print
		#print "new right motor port:",
		#print motor_port
		#print
		
		if (self.brainstormsClient != None):
			
			update = {'motor_port_right': motor_port}
			
			self.brainstormsClient.sendCommand('update', default_data=update)
	
	
	##################################################################
	
	def updateMotorSpinReversed(self):
		
		#print
		#print
		#print
		#print "Updating motors mounted backwards:",
		
		motors_mounted_backwards = self.checkBoxMotorSpinReversed.isChecked()
		
		#print motors_mounted_backwards
		#print
		#print
		#print
		
		if (self.brainstormsClient != None):
			
			update = {'motors_mounted_backwards': motors_mounted_backwards}
			
			self.brainstormsClient.sendCommand('update', default_data=update)
	
	
	##################################################################
	
	def enableHelicopterHover(self):
		
		if self.pushButtonHelicopterFlyForward.isChecked():
			self.pushButtonHelicopterFlyForward.setChecked(False)
			self.disableHelicopterFlyForward()
		
		self.helicopter.hover(duration=None)
		self.current_helicopter_state = 'hover'
		
		self.disconnect(self.pushButtonHelicopterHover, \
							QtCore.SIGNAL("clicked()"), \
							self.enableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterHover, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disableHelicopterHover)
		
		#if self.pushButtonHelicopterFlyForward.isChecked():
			#self.pushButtonHelicopterFlyForward.toggle()
			##self.disableHelicopterFlyForward()
	
	
	##################################################################
	
	def disableHelicopterHover(self):
		
		self.helicopter.neutral()
		self.current_helicopter_state = 'neutral'
		
		self.disconnect(self.pushButtonHelicopterHover, \
							QtCore.SIGNAL("clicked()"), \
							self.disableHelicopterHover)
		
		self.connect(self.pushButtonHelicopterHover, \
			          QtCore.SIGNAL("clicked()"), \
			          self.enableHelicopterHover)
	
	
	##################################################################
	
	def enableHelicopterFlyForward(self):
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
			self.disableHelicopterHover()
		
		self.helicopter.fly_forward(duration=None)
		self.current_helicopter_state = 'fly_forward'
		
		self.disconnect(self.pushButtonHelicopterFlyForward, \
							QtCore.SIGNAL("clicked()"), \
							self.enableHelicopterFlyForward)
		
		self.connect(self.pushButtonHelicopterFlyForward, \
			          QtCore.SIGNAL("clicked()"), \
			          self.disableHelicopterFlyForward)
		
		#if self.pushButtonHelicopterHover.isChecked():
			#self.pushButtonHelicopterHover.toggle()
			##self.disableHelicopterHover()
	
	
	##################################################################
	
	def disableHelicopterFlyForward(self):
		
		self.helicopter.neutral()
		self.current_helicopter_state = 'neutral'
		
		self.disconnect(self.pushButtonHelicopterFlyForward, \
							QtCore.SIGNAL("clicked()"), \
							self.disableHelicopterFlyForward)
		
		self.connect(self.pushButtonHelicopterFlyForward, \
			          QtCore.SIGNAL("clicked()"), \
			          self.enableHelicopterFlyForward)
	
	
	##################################################################
	
	def landHelicopter(self):
		
		self.helicopter.neutral()
		self.current_helicopter_state = 'neutral'
		
		if self.pushButtonHelicopterHover.isChecked():
			self.pushButtonHelicopterHover.setChecked(False)
			self.disableHelicopterHover()
		if self.pushButtonHelicopterFlyForward.isChecked():
			self.pushButtonHelicopterFlyForward.setChecked(False)
			self.disableHelicopterFlyForward()
	
	
	##################################################################
	
	def driveWheelchairForward(self):
		print "WheelchairForward"
		speed = self.dialWheelchairSpeed.value()
		self.wheelchair.sendCommand(speed, 'forward')
	
	def driveWheelchairReverse(self):
		#print "WheelchairReverse"
		speed = self.dialWheelchairSpeed.value()
		self.wheelchair.sendCommand(speed, 'reverse')
	
	def driveWheelchairLeft(self):
		#print "WheelchairLeft"
		speed = self.dialWheelchairSpeed.value()
		self.wheelchair.sendCommand(speed, 'left')
	
	def driveWheelchairRight(self):
		#print "WheelchairRight"
		speed = self.dialWheelchairSpeed.value()
		self.wheelchair.sendCommand(speed, 'right')
	
	def stopWheelchair(self):
		print "stopWheelchair"
		speed = self.dialWheelchairSpeed.value()
		self.wheelchair.sendCommand(speed, 'stop')
	
	
	##################################################################
	
	def updateWheelchairSpeed(self, value):
		
		if self.DEBUG:
			print "DEBUG [Brainstorms:Interface]: updateWheelchairSpeed():",
			print value
	
	
	##################################################################
	
	def updateRobotSpeed(self, new_speed=None):
		
		
		#print
		#print "updateRobotSpeed"
		#print "drive_state:",
		#print self.drive_state
		#print "left.isDown:",
		#print self.pushButtonTurnLeft.isDown()
		#print "not left.isFlat:",
		#print not self.pushButtonTurnLeft.isFlat()
		#print
		#print "forward.isDown:",
		#print self.pushButtonForward.isDown()
		#print "not forward.isFlat:",
		#print not self.pushButtonForward.isFlat()
		#print
		#print "right.isDown:",
		#print self.pushButtonTurnRight.isDown()
		#print "not right.isFlat:",
		#print not self.pushButtonTurnRight.isFlat()
		#print
		#print "reverse.isDown:",
		#print self.pushButtonReverse.isDown()
		#print "not reverse.isFlat:",
		#print not self.pushButtonReverse.isFlat()
		#print
		
		
		if new_speed == None:
		
			concentration=self.progressBarConcentration.value()
			relaxation=self.progressBarRelaxation.value()
			
			new_speed = self.calculateSpeed(concentration, relaxation)
		
		
		# Update GUI
		if self.pushButtonSpeedEnable.isChecked():
			self.progressBarSpeed.setValue(new_speed)
		
		
		# If there is a change between the new and current speeds
		# and either the robot is currently driving
		# or the "speed control" button is enabled,
		# then send the updated speed to the robot
		if ((self.current_speed != new_speed) and \
			 ((self.drive_state != 'stop_motors') or \
			  (self.pushButtonSpeedEnable.isChecked()))):
			
			if (new_speed == 0):
				self.current_speed = new_speed
				self.stopMotors()
			else:
				if ((self.brainstormsClient != None) and \
				    (self.pushButtonSpeedEnable.isChecked())):
					
					if ((self.pushButtonTurnLeft.isDown()) or \
					    (not self.pushButtonTurnLeft.isFlat())):
						self.pushButtonTurnLeft.setDown(True)
						self.brainstormsClient.sendCommand('turn_left', power=new_speed)
						self.drive_state = 'turn_left'
					
					if ((self.pushButtonForward.isDown()) or \
					    (not self.pushButtonForward.isFlat())):
						self.pushButtonForward.setDown(True)
						self.brainstormsClient.sendCommand('drive_forward', power=new_speed)
						self.drive_state = 'drive_forward'
					
					if ((self.pushButtonReverse.isDown()) or \
					    (not self.pushButtonReverse.isFlat())):
						self.pushButtonReverse.setDown(True)
						self.brainstormsClient.sendCommand('drive_reverse', power=new_speed)
						self.drive_state = 'drive_reverse'
					
					if ((self.pushButtonTurnRight.isDown()) or \
					    (not self.pushButtonTurnRight.isFlat())):
						self.pushButtonTurnRight.setDown(True)
						self.brainstormsClient.sendCommand('turn_right', power=new_speed)
						self.drive_state = 'turn_right'
		
		
		self.current_speed = new_speed
	
	
	##################################################################
	
	def updateHelicopterSpeed(self, new_speed=None):
		
		if new_speed == None:
		
			concentration=self.progressBarHelicopterConcentration.value()
			relaxation=self.progressBarHelicopterRelaxation.value()
			
			new_speed = self.calculateSpeed(concentration, relaxation)
		
		
		# Update GUI
		if self.pushButtonHelicopterSpeedEnable.isChecked():
			self.progressBarHelicopterSpeed.setValue(new_speed)
			
			if ((new_speed > 0) and \
			    (self.current_helicopter_state == 'neutral') and \
			    (self.helicopter != None)):
				self.enableHelicopterHover()
			
			elif ((new_speed == 0) and \
			      (self.current_helicopter_state != 'neutral') and \
			      (self.helicopter != None)):
				self.landHelicopter()
		
		
		self.current_speed = new_speed
	
	
	##################################################################
	
	def updateWheelchairSpeed(self, new_speed=None):
		
		if new_speed == None:
		
			concentration=self.progressBarWheelchairConcentration.value()
			relaxation=self.progressBarWheelchairRelaxation.value()
			
			new_speed = self.calculateSpeed(concentration, relaxation)
		
		
		# Update GUI
		if self.pushButtonWheelchairSpeedEnable.isChecked():
			self.progressBarWheelchairSpeed.setValue(new_speed)
		
		
		self.current_speed = new_speed
	
	
	##################################################################
	
	def calculateSpeed(self, concentration, relaxation):
		
		speed = 0
		
		thresholds = THINKGEAR_POWER_THRESHOLDS
		
		match = int(concentration)
		
		while ((match not in thresholds['concentration'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		
		if match in thresholds['concentration'].keys():
			speed = thresholds['concentration'][match]
		
		
		match = int(relaxation)
		
		while ((match not in thresholds['relaxation'].keys()) and \
			    (match >= 0)):
			match -= 1
		
		if match in thresholds['relaxation'].keys():
			speed = speed + thresholds['relaxation'][match]
		
		
		# LEGO Mindstorms power settings cannot exceed 100
		# and don't drive well with levels less than 50
		if (speed > 100):
			speed = 100
		elif (speed < 50):
			speed = 0
		
		
		return(speed)
	
	
	##################################################################
	
	def processPacketThinkGear(self, packet):
		
		if ('eSense' in packet.keys()):
			
			# We process eyeblinks here because we receive
			# eSense packets once per second. Its a convenient
			# means of processing at this frequency without
			# setting an additional timer thread for the program
			
			self.processEyeBlinks()
			
			if ('attention' in packet['eSense'].keys()):
				if self.pushButtonConcentrationEnable.isChecked():
					self.progressBarConcentration.setValue(packet['eSense']['attention'])
				if self.pushButtonHelicopterConcentrationEnable.isChecked():
					self.progressBarHelicopterConcentration.setValue(packet['eSense']['attention'])
				if self.pushButtonWheelchairConcentrationEnable.isChecked():
					self.progressBarWheelchairConcentration.setValue(packet['eSense']['attention'])
			
			if ('meditation' in packet['eSense'].keys()):
				if self.pushButtonRelaxationEnable.isChecked():
					self.progressBarRelaxation.setValue(packet['eSense']['meditation'])
				if self.pushButtonHelicopterRelaxationEnable.isChecked():
					self.progressBarHelicopterRelaxation.setValue(packet['eSense']['meditation'])
				if self.pushButtonWheelchairRelaxationEnable.isChecked():
					self.progressBarWheelchairRelaxation.setValue(packet['eSense']['meditation'])
		
		
		# Eye Blinks
		if ('blinkStrength' in packet.keys()):
			self.blinks[time.time()] = packet
		
		
		## Emotiv Cognitiv support
		#if ('cognitiv' in packet.keys()):
			
			#if (('currentAction' in packet['cognitiv'].keys()) and \
			    #('currentActionPower' in packet['cognitiv'].keys()) and \
			    #(self.pushButtonRobotConnect.text != 'Connect')):
				#if self.pushButtonConcentrationEnable.isChecked():
					#self.progressBarConcentration.setValue( int(packet['cognitiv']['currentActionPower'] * 100 )
				#if self.pushButtonHelicopterConcentrationEnable.isChecked():
					#self.progressBarHelicopterConcentration.setValue( int(packet['cognitiv']['currentActionPower'] * 100 )
				#if self.pushButtonWheelchairConcentrationEnable.isChecked():
					#self.progressBarWheelchairConcentration.setValue( int(packet['cognitiv']['currentActionPower'] * 100 )
		
		
		#if ('cognitiv' in packet.keys()):
			
			#if (('currentAction' in packet['cognitiv'].keys()) and \
			    #('currentActionPower' in packet['cognitiv'].keys()) and \
			    #(self.pushButtonRobotConnect.text != 'Connect')):
				
				# Rotate Left
				#if ((int(packet['cognitiv']['currentAction']) == 128) and \
				    #(packet['cognitiv']['currentActionPower'] >= 0.2)):
					#self.sendMessageOne()
				
				# Rotate Right
				#if ((int(packet['cognitiv']['currentAction']) == 256) and \
				    #(packet['cognitiv']['currentActionPower'] >= 0.2)):
					#self.sendMessageTwo()
				
				# Lift
				#if ((int(packet['cognitiv']['currentAction']) == 8) and \
				    #(packet['cognitiv']['currentActionPower'] >= 0.2)):
					#self.sendMessageThree()
				
				# Drop
				#if ((int(packet['cognitiv']['currentAction']) == 16) and \
				    #(packet['cognitiv']['currentActionPower'] >= 0.2)):
					#self.sendMessageFour()
		
		
		self.updateRobotSpeed()
		self.updateHelicopterSpeed()
		self.updateWheelchairSpeed()
	
	
	##################################################################
	
	def processEyeBlinks(self):
		
		current_time = time.time()
		
		keys_to_delete = []
		
		for timestamp in self.blinks:
			if current_time - timestamp > BLINK_DETECTION_VALID_RANGE:
				keys_to_delete.append(timestamp)
		
		for timestamp in keys_to_delete:
			del(self.blinks[timestamp])
		
		
		try:
			blink_threshold = int(self.lineEditBlinkDetectionThreshold.text())
		except:
			blink_threshold = BLINK_DETECTION_THRESHOLD
		
		self.progressBarBlinkDetection.setMaximum( blink_threshold )
		
		
		blinks = len(self.blinks)
		if blinks > blink_threshold:
			blinks = blink_threshold
      
		
		self.progressBarBlinkDetection.setValue( blinks )
		
		
		if ((self.checkBoxBlinkDetectionEnabled.isChecked()) and \
			 (blinks >= blink_threshold)):
			
			self.rotateControlButtons()
	
	
	##################################################################
	
	def rotateControlButtons(self):
		
		# Robotics
		if ((self.tabWidget.currentIndex() == \
			  self.tabWidget.indexOf(self.tabRobotics)) and \
			 (self.brainstormsClient != None)):
			
			
			# Handle changes differntly depending if already moving
			if self.drive_state == 'stop_motors':
			
				# Forward -> Right -> Reverse -> Left -> Forward
				
				if not self.pushButtonForward.isFlat():
					self.pushButtonForward.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setFlat(False)
				
				elif not self.pushButtonTurnRight.isFlat():
					self.pushButtonTurnRight.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setFlat(False)
				
				elif not self.pushButtonReverse.isFlat():
					self.pushButtonReverse.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setFlat(False)
				
				elif not self.pushButtonTurnLeft.isFlat():
					self.pushButtonTurnLeft.setFlat(True)
					self.pushButtonForward.setFlat(False)
					
					if BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setFlat(False)
			
			
			else:
				
				# Forward -> Right -> Reverse -> Left -> Forward
				
				if self.pushButtonForward.isDown():
					#self.pushButtonForward.emit(QtCore.SIGNAL("released()"))
					self.pushButtonForward.setDown(False)
					self.pushButtonForward.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setDown(True)
						self.pushButtonTurnRight.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setDown(True)
						self.pushButtonReverse.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setDown(True)
						self.pushButtonTurnLeft.setFlat(False)
				
				
				elif self.pushButtonTurnRight.isDown():
					#self.pushButtonTurnRight.emit(QtCore.SIGNAL("released()"))
					self.pushButtonTurnRight.setDown(False)
					self.pushButtonTurnRight.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setDown(True)
						self.pushButtonReverse.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setDown(True)
						self.pushButtonTurnLeft.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setDown(True)
						self.pushButtonForward.setFlat(False)
				
				
				elif self.pushButtonReverse.isDown():
					#self.pushButtonReverse.emit(QtCore.SIGNAL("released()"))
					self.pushButtonReverse.setDown(False)
					self.pushButtonReverse.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_LEFT:
						self.pushButtonTurnLeft.setDown(True)
						self.pushButtonTurnLeft.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setDown(True)
						self.pushButtonForward.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setDown(True)
						self.pushButtonTurnRight.setFlat(False)
				
				
				elif self.pushButtonTurnLeft.isDown():
					#self.pushButtonTurnLeft.emit(QtCore.SIGNAL("released()"))
					self.pushButtonTurnLeft.setDown(False)
					self.pushButtonTurnLeft.setFlat(True)
					
					if BLINK_DETECTION_INCLUDE_FORWARD:
						self.pushButtonForward.setDown(True)
						self.pushButtonForward.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_RIGHT:
						self.pushButtonTurnRight.setDown(True)
						self.pushButtonTurnRight.setFlat(False)
					elif BLINK_DETECTION_INCLUDE_REVERSE:
						self.pushButtonReverse.setDown(True)
						self.pushButtonReverse.setFlat(False)
		
		
		self.blinks = {} # Reset all blinks after a rotation
	
	
	##################################################################
	
	def sendFeedback(self):
		
		values = {}
		
		values['name'] = str(self.lineEditFeedbackName.text())
		values['email'] = str(self.lineEditFeedbackEmail.text())
		values['comment'] = str(self.textEditFeedback.toPlainText())
		
		values['subject'] = '[brainstorms feedback]'
		values['capcha_contact'] = 'brainstorms'
		
		
		url_data = urllib.urlencode(values)
		
		try:
			page = urllib.urlopen(BRAINSTORMS_FEEDBACK_URL, url_data)
			
			reply = QtGui.QMessageBox.information( \
		              self, \
		              'Feedback Sent', \
		              'Thank you for your feedback', \
		              'OK')
			
			self.lineEditFeedbackName.setText('')
			self.lineEditFeedbackEmail.setText('')
			self.textEditFeedback.setText('')
		
		except:
			reply = QtGui.QMessageBox.information( \
		              self, \
		              'Feedback Sent', \
		              'We\'re sorry but there was an error submitting your feedback.\nPlease email contact@puzzlebox.info instead.', \
		              'OK')
	
	
	##################################################################
	
	def closeEvent(self, event):
		
		quit_message = "Are you sure you want to exit the program?"
		
		reply = QtGui.QMessageBox.question( \
		           self, \
		          'Quit Puzzlebox Brainstorms', \
		           quit_message, \
		           QtGui.QMessageBox.Yes, \
		           QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			
			if self.brainstormsClient != None:
				self.stopMotors()
				self.brainstormsClient.socket.flush()
				
				if self.brainstormsServer != None:
					
					if self.brainstormsServer.rc == None:
						
						device_address = str(self.comboBoxRobotPortSelect.currentText())
						self.brainstormsServer.executeCommand( \
							'stop_motors')
						
					else:
						self.brainstormsServer.rc.run('stop_motors')
			
			
			event.accept()
		
		else:
			event.ignore()


#####################################################################
# Functions
#####################################################################

#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
	
	#log = puzzlebox_logger.puzzlebox_logger(logfile='client_interface')
	log = None
	
	app = QtGui.QApplication(sys.argv)
	
	window = puzzlebox_brainstorms_client_interface(log, DEBUG)
	window.show()
	
	sys.exit(app.exec_())

