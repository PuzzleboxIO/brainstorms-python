#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Configuration
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """\
Last Update: 2012.08.20

"""

import os, sys
#import pygame

#####################################################################
# General configuration
#####################################################################

DEBUG = 1

ENABLE_PYSIDE = True

ENABLE_CONTROL_PANEL = True

# Discrete control drives the robot for a set time period per detection.
# Setting Variable control to "True" will drive the robot in a
# particular direction for as long as the detection occurs
BRAINSTORMS_VARIABLE_CONTROL_DURATION = True

BLINK_DETECTION_ENABLED = True
BLINK_DETECTION_THRESHOLD = 6 # 6 blinks detected within the valid range
BLINK_DETECTION_VALID_RANGE = 2 # 2 seconds

BLINK_DETECTION_INCLUDE_FORWARD = True
BLINK_DETECTION_INCLUDE_LEFT = True
BLINK_DETECTION_INCLUDE_RIGHT = True
BLINK_DETECTION_INCLUDE_REVERSE = True

BRAINSTORMS_CONFIGURATION_FILE_PATH = 'puzzlebox_brainstorms_configuration.ini'

if (sys.platform != 'win32'):
	if not os.path.exists(BRAINSTORMS_CONFIGURATION_FILE_PATH):
		BRAINSTORMS_CONFIGURATION_FILE_PATH = \
			os.path.join('/etc/puzzlebox_synapse', BRAINSTORMS_CONFIGURATION_FILE_PATH)


#####################################################################
# Logging
#####################################################################

LOG_LEVEL_DEBUG = 2
LOG_LEVEL_INFO = 1
LOG_LEVEL_ERROR = 0
LOG_LEVEL_DISABLE = -1

DEFAULT_LOG_LEVEL = LOG_LEVEL_DEBUG
DEFAULT_LOGFILE = 'brainstorms'

LOGFILE_DIR = '/var/log/puzzlebox'
LOGFILE_SUFFIX = '.log'
LOGFILE_SUFFIX_DEBUG = '_debug.log'
LOGFILE_SUFFIX_INFO = '_info.log'
LOGFILE_SUFFIX_ERROR = '_error.log'

SPLIT_LOGFILES = False


#####################################################################
# Network addresses
#####################################################################

BRAINSTORMS_SERVER_INTERFACE = '' # listen on all of server's network interfaces
BRAINSTORMS_SERVER_HOST = '127.0.0.1' # localhost
BRAINSTORMS_SERVER_PORT = 8194

THINKGEAR_SERVER_INTERFACE = '' # listen on all of server's network interfaces
THINKGEAR_SERVER_HOST = '127.0.0.1'
THINKGEAR_SERVER_PORT = 13854


#####################################################################
# NXT Control configuration
#####################################################################

AUTOCONNECT_TO_NXT_DEVICE = False

DEFAULT_NXT_POWER_LEVEL = 80

DEFAULT_NXT_BLUETOOTH_DEVICE_WINDOWS = 'COM1'
DEFAULT_NXT_BLUETOOTH_DEVICE_LINUX = '/dev/rfcomm0'

if (sys.platform == 'win32'):
	NXT_BLUETOOTH_DEVICE = DEFAULT_NXT_BLUETOOTH_DEVICE_WINDOWS
else:
	NXT_BLUETOOTH_DEVICE = DEFAULT_NXT_BLUETOOTH_DEVICE_LINUX

NXT_MOTORS_MOUNTED_BACKWARDS = False
NXT_MOTOR_PORT_LEFT = 'b'
NXT_MOTOR_PORT_RIGHT = 'a'
NXT_DEFAULT_RC_COMMAND = 'test_drive'


#####################################################################
#iRobot Configuration
#####################################################################

IROBOT_MOVE_DELAY = 1
IROBOT_TURN_DELAY = 0.5

IROBOT_SERIAL_TIMEOUT = 2

DEFAULT_IROBOT_BLUETOOTH_DEVICE_WINDOWS = 'COM40'
DEFAULT_IROBOT_BLUETOOTH_DEVICE_LINUX = '/dev/rfcomm0'

if (sys.platform == 'win32'):
	IROBOT_BLUETOOTH_DEVICE = DEFAULT_IROBOT_BLUETOOTH_DEVICE_WINDOWS
else:
	IROBOT_BLUETOOTH_DEVICE = DEFAULT_IROBOT_BLUETOOTH_DEVICE_LINUX

IROBOT_DEFAULT_RC_COMMAND = 'test_drive'

IROBOT_VELOCITY_MAX = 500  # mm/s
IROBOT_VELOCITY_SLOW = 15
IROBOT_VELOCITY_FAST = 350
IROBOT_TURN_SPEED = 300


#####################################################################
# RC Car Control configuration
#####################################################################

DEFAULT_RC_CAR_POWER_LEVEL = 80

DEFAULT_RC_CAR_DEVICE_WINDOWS = 'COM1'
DEFAULT_RC_CAR_DEVICE_LINUX = '/dev/rfcomm0'

if (sys.platform == 'win32'):
	RC_CAR_DEVICE = DEFAULT_RC_CAR_DEVICE_WINDOWS
else:
	RC_CAR_DEVICE = DEFAULT_RC_CAR_DEVICE_LINUX


#####################################################################
# Helicopter configuration
#####################################################################

COMMAND_PACKET = {
	'default_neutral':      '\x00\x00\x00\xaa\x05\xff\x09\xff\x0d\xff\x13\x54\x14\xaa',  # default neutral setting to use for all commands
	'default_full_thrust':  '\x00\x00\x03\x54\x05\xff\x09\xff\x0d\xff\x13\x54\x14\xaa',  # new controll set to highest throttle (no changes to trim)
	#'neutral':             '\x00\x00\x00\xfa\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa',  # 0.4.5 neutral setting to use for all commands
	'neutral':              '\x00\x00\x00\xae\x05\xff\x09\xff\x0d\xff\x13\x54\x14\xaa',  # default neutral setting to use for all commands
	'no_thrust':            '\x00\x00\x00\x5a\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa',  # lowest trim setting for throttle
	'minimum_thrust':       '\x00\x00\x00\xca\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa',  # lowest trim level at which throttle kicks in
	'minimum_thrust_minus_one': '\x00\x00\x00\xc6\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa',  # lowest trim level at which throttle kicks in
	'maximum_thrust':       '\x00\x00\x03\x54\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa',  # maximum possible throttle and trim
	'fifty_percent_thrust': '\x00\x00\x01\x7d\x05\xc5\x09\xde\x0e\x0b\x13\x54\x14\xaa', # calculated 50% throttle
	'test_packet':          '\x00\x00\x03\x54\x06\x15\x09\xca\x0e\x2f\x13\x54\x14\xaa', # test packet from saleae logic screenshot
	'maximum_forward':      '\x00\x00\x00\x5a\x05\xc5\x0b\x54\x0e\x0b\x13\x54\x14\xaa', # maximum possible elevator and trim
	    #'fly_forward':      '\x00\x00\x01\x7d\x05\xc5\x0a\xde\x0e\x0b\x13\x54\x14\xaa', # 0.4.5 fly_forward settings 
	    'fly_forward':      '\x00\x00\x01\x7d\x05\xc5\x0a\xde\x0e\x0b\x13\x54\x14\xaa', 
}

COMMAND_ACTIVATE = 'fifty_percent_thrust'
# COMMAND_ACTIVATE = 'maximum_thrust'
# COMMAND_ACTIVATE = 'minimum_thrust'
# COMMAND_ACTIVATE = 'fly_forward'


#####################################################################
# Wheelchair configuration
#####################################################################

WHEELCHAIR_CONTROL_EEG = True


#####################################################################
# Server configuration
#####################################################################

BRAINSTORMS_DELIMITER = '\r'

#TWISTED_SERVER_MAX_COMPONENTS = 16


#####################################################################
# Client configuration
#####################################################################

CLIENT_NO_REPLY_WAIT = 5 # how many seconds before considering a component dead

#TWISTED_CLIENT_MAX_CONNECTION_ATTEMPTS = 5


#####################################################################
# ThinkGear Connect configuration
#####################################################################

THINKGEAR_DELIMITER = '\r'

THINKGEAR_CONFIGURATION_PARAMETERS = {"enableRawOutput": False, "format": "Json"}

THINKGEAR_AUTHORIZATION_ENABLED = False

THINKGEAR_AUTHORIZATION_REQUEST = { \
	"appName": "Puzzlebox Brainstorms", \
	"appKey": "2e285d7bd5565c0ea73e7e265c73f0691d932408"
}


#####################################################################
# ThinkGear Connect Server Emulator configuration
#####################################################################

THINKGEAR_ENABLE_SIMULATE_HEADSET_DATA = True

THINKGEAR_BLINK_FREQUENCY_TIMER = 6 # blink every 6 seconds
                                    # (6 seconds is listed by Wikipedia
                                    # as being the average number of times
                                    # an adult blinks in a laboratory setting)

THINKGEAR_DEFAULT_SAMPLE_WAVELENGTH = 30 # number of seconds from 0 to max
                                         # and back to 0 for any given
                                         # detection value below


#####################################################################
# Client Interface configuration [Qt]
#####################################################################

THINKGEAR_POWER_THRESHOLDS = { \
	
	'concentration': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 60, \
		50: 65, \
		60: 70, \
		70: 75, \
		75: 80, \
		80: 85, \
		90: 90, \
		100: 90, \
		}, \
	
	'relaxation': { \
		0: 0, \
		10: 0, \
		20: 0, \
		30: 0, \
		40: 0, \
		50: 10, \
		60: 10, \
		70: 15, \
		80: 15, \
		90: 20, \
		100: 20, \
		}, \
	
} # THINKGEAR_POWER_THRESHOLDS


#####################################################################
# Flash socket policy handling
#####################################################################

FLASH_POLICY_FILE_REQUEST = \
        '<policy-file-request/>%c' % 0 # NULL byte termination
FLASH_SOCKET_POLICY_FILE = '''<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
   <site-control permitted-cross-domain-policies="all" />
   <allow-access-from domain="*" to-ports="%i" />
</cross-domain-policy>%c''' % (THINKGEAR_SERVER_PORT, 0)


#####################################################################
# Configuration File Parser
#####################################################################

if os.path.exists(BRAINSTORMS_CONFIGURATION_FILE_PATH):
	
	file = open(BRAINSTORMS_CONFIGURATION_FILE_PATH, 'r')
	
	for line in file.readlines():
		line = line.strip()
		if len(line) == 0:
			continue
		if line[0] == '#':
			continue
		if line.find('=') == -1:
			continue
		if (line == "NXT_BLUETOOTH_DEVICE = ''") or \
		   (line == "IROBOT_BLUETOOTH_DEVICE = ''") or \
		   (line == "RC_CAR_DEVICE = ''"):
			# use operating system default if device not set manually
			continue
		try:
			exec line
		except:
			if DEBUG:
				print "Error recognizing Puzzlebox Brainstorms configuration option:",
				print line

