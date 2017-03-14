#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Puzzlebox - Brainstorms - Helicopter Control
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html

__changelog__ = """2012.06.14
"""

import sys, time
import signal
import serial

##try:
##	import PySide as PyQt4
##	from PySide import QtCore
##except:
##	print "Using PyQt4 module"
##	from PyQt4 import QtCore
##else:
##	print "Using PySide module"

import Configuration as configuration

if configuration.ENABLE_PYSIDE:
	try:
		import PySide as PyQt4
		from PySide import QtCore
	except Exception, e:
		print "ERROR: Exception importing PySide:",
		print e
		configuration.ENABLE_PYSIDE = False
	else:
		print "INFO: [Brainstorms:Helicopter_Control] Using PySide module"

if not configuration.ENABLE_PYSIDE:
	print "INFO: [Brainstorms:Helicopter_Control] Using PyQt4 module"
	from PyQt4 import QtCore

#import Puzzlebox.Synapse.Protocol as protocol
#from Puzzlebox.Synapse import Protocol

#####################################################################
# Globals
#####################################################################

DEBUG = 2

DEFAULT_COMMAND = 'dump_packets'

COMMAND_ACTIVATE = configuration.COMMAND_ACTIVATE

SERIAL_DEVICE = '/dev/ttyUSB0'
#SERIAL_DEVICE = '/dev/ttyACM0'
#DEFAULT_SERIAL_BAUDRATE = 115200 # This is the closest "standard" baud rate the USB-to-Serial device will support
#DEFAULT_SERIAL_BAUDRATE = 125000 # This is the speed reported by the forum post
#DEFAULT_SERIAL_BAUDRATE = 128000 # This is the next closest somewhat commonly-found baud rate (though not supported by device)
DEFAULT_SERIAL_BAUDRATE = 133333 # This is the speed reported by the logic analyzer
#DEFAULT_SERIAL_BAUDRATE = 230400 # This is the next highest "standard" baud rate the USB-to-Serial device will support
DEFAULT_MODE = 'read'

PROTOCOL_SYNC_TIME = 5
PROTOCOL_SYNC_HEAD1 = '\x00'
PROTOCOL_SYNC_HEAD2 = '\x00'
PROTOCOL_ADD_SYNC_TO_HEAD = False
PROTOCOL_ADD_SYNC_TO_TAIL = False
PACKET_LENGTH = 14
PAYLOAD_MINIMUM_LENGTH = 12
PACKET_READ_SIZE = 14
ECHO_ON = False

#DEVICE_BUFFER_TIMER = 22  # Frame cycle 22ms
DEVICE_BUFFER_TIMER = 21  # Frame cycle 22ms

# Protocol Specification
#
#	000000a605ff0a060dff135414aa
#	AaAaBbbbCcccDdddEeee______Ff
#	
#	Aa - Frame sync bytes
#	Bbbb - Throttle bytes (4 decimal values per trim step)
#	Cccc - Aileron bytes (3 or 4 decimal values per trim step)
#	Dddd - Elevator bytes (3 or 4 decimal values per trim step)
#	Eeee - Rudder bytes (2 decimal values per trim step)
#	Ff - End of Frame byte
#	____ - Unused/Unknown
#
#
#	Example throttle bytes
#
#0354 : +20 highest throttle stick setting and trim [852]
#
#00fa:  +20 [250]
#00f6:  +19
#00f2:  +18
#00ee:  +17
#00ea:  +16
#00e6:  +15
#00e2:  +14
#00de:  +13
#00da:  +12
#00d6:  +11
#00d2:  +10
#00ce:  +9
#00ca:  +8
#00c6:  +7
#00c2:  +6
#00be:  +5
#00ba:  +4
#00b6:  +3
#00b2:  +2 [178]
#00ae:  +1 [174]
#00aa:  lowest throttle stick setting [170]
#00a6:  -1 [166]
#00a2:  -2
#009e:  -3
#009a:  -4
#0096:  -5
#0092:  -6
#008e:  -7
#008a:  -8
#0086:  -9
#0082:  -10
#007e:  -11
#007a:  -12
#0076:  -13
#0072:  -14
#006e:  -15
#006a:  -16
#0066:  -17
#0062:  -18
#005e:  -19
#005a:  -20 [90]



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

DEFAULT_COMMAND_PACKET = COMMAND_PACKET['neutral']

#####################################################################
# Classes
#####################################################################

class puzzlebox_brainstorms_helicopter_control(QtCore.QThread):
	
	def __init__(self, \
	             device_address=SERIAL_DEVICE, \
	             command=DEFAULT_COMMAND, \
	             DEBUG=DEBUG, \
	             parent=None):
		
		QtCore.QThread.__init__(self, parent)
		
		self.log = None
		self.DEBUG = DEBUG
		self.parent = parent
		
		self.device_address = device_address
		self.command = command
		self.mode = DEFAULT_MODE
		
		self.serial_device = None
		self.protocol = None
		
		
		#self.configureRemote()
	
	
	##################################################################
	
	def configureRemote(self):
		
		self.serial_device = \
			SerialDevice( \
				self.log, \
				device_address=self.device_address, \
				mode=self.mode, \
				DEBUG=self.DEBUG, \
				parent=self)
		
		self.serial_device.start()
		
		
		self.protocol = \
			ProtocolHandler( \
				self.log, \
				self.serial_device, \
				mode=self.mode, \
				DEBUG=self.DEBUG, \
				parent=self)
		
		self.protocol.start()
	
	
	##################################################################
	
	def processPacket(self, packet):
		
		if self.DEBUG:
			print "data_payload:",
			#print packet['data_payload']
			print packet['data_payload'].encode("hex")
			
			#if packet['data_payload'].encode("hex") == '80acdf22cdb08b8d54':
				#print True
				#import cPickle as pickle
				#file = open('packet.data', 'w')
				#pickle.dump(packet['data_payload'], file)
				#file.close()
				#sys.exit(app.exec_())
		
		#if (packet != {}):
			#self.packet_queue.append(packet)
			###self.sendPacketQueue()
		
		if (self.parent != None):
			self.parent.processPacket(self.protocol.data_packet)
	
	
	##################################################################
	
	def dump_packets(self):
		
		pass
	
	
	##################################################################
	
	def sync_to_helicopter(self):
		
		self.protocol.command_packet = COMMAND_PACKET['no_thrust']
		QtCore.QThread.msleep(PROTOCOL_SYNC_TIME * 1000) # 4 seconds minimum to sync
	
	
	##################################################################
	
	def neutral(self):
		
		if self.DEBUG:
			print "--> RC Helicopter Command: neutral"
		
		#self.protocol.command_packet = COMMAND_PACKET['neutral']
		self.protocol.command_packet = COMMAND_PACKET['no_thrust']
	
	
	##################################################################
	
	def test_packet(self):
		
		if self.DEBUG:
			print "--> RC Helicopter Command: test_packet"
		
		self.protocol.command_packet = COMMAND_PACKET['test_packet']
	
	
	##################################################################
	
	def test_mode(self):
		
		if self.DEBUG:
			print "--> RC Helicopter Command: test_mode"
		
		#self.sync_to_helicopter()
		
		self.protocol.command_packet = COMMAND_PACKET['minimum_thrust']
		QtCore.QThread.msleep(2 * 1000) # 1 second
		
		self.protocol.command_packet = COMMAND_PACKET['no_thrust']
	
	
	##################################################################
	
	def hover(self, duration=2):
		
		if self.DEBUG:
			print "--> RC Helicopter Command: hover"
		
		#self.sync_to_helicopter()
		
		#self.protocol.command_packet = COMMAND_PACKET['fifty_percent_thrust']
		##self.protocol.command_packet = COMMAND_PACKET['maximum_thrust']
		
		self.protocol.command_packet = COMMAND_PACKET[COMMAND_ACTIVATE]
		
		if duration != None:
			QtCore.QThread.msleep(duration * 1000)
			
			self.protocol.command_packet = COMMAND_PACKET['no_thrust']
	
	
	##################################################################
	
	def fly_forward(self, duration=2):
		
		if self.DEBUG:
			print "--> RC Helicopter Command: fly_forward"
		
		#self.sync_to_helicopter()
		
		self.protocol.command_packet = COMMAND_PACKET['fly_forward']
		
		if duration != None:
			QtCore.QThread.msleep(duration * 1000)
			
			self.protocol.command_packet = COMMAND_PACKET['no_thrust']
	
	
	##################################################################
	
	def processCommand(self):
		
		if (self.command == 'dump_packets') or (self.command == 'read'):
			self.mode = 'read'
		else:
			self.mode = 'write'
		
		
		self.configureRemote()
		
		
		if (self.command == 'dump_packets'):
			self.mode = 'read'
			self.dump_packets()
		
		elif (self.command == 'neutral'):
			self.mode = 'write'
			self.neutral()
		
		elif (self.command == 'test_packet'):
			self.mode = 'write'
			self.test_packet()
		
		elif (self.command == 'test_mode'):
			self.mode = 'write'
			self.sync_to_helicopter()
			self.test_mode()
		
		elif (self.command == 'hover'):
			self.mode = 'write'
			self.sync_to_helicopter()
			self.hover()
		
		elif (self.command == 'fly_forward'):
			self.mode = 'write'
			self.sync_to_helicopter()
			self.fly_forward(duration=2)
	
	
	##################################################################
	
	def stop(self):
		
		#self.connection.close()
		pass
	
	
	##################################################################
	
	def run(self):
		
		if self.DEBUG:
			print "<---- [%s] Main thread running" % "Helicopter Remote"
		
		
		self.processCommand()
		
		self.exec_()
	
	
	##################################################################
	
	def exitThread(self, callThreadQuit=True):
		
		try:
			self.emulationTimer.stop()
		except:
			pass
		
		if self.serial_device != None:
			self.serial_device.exitThread()
		
		if self.protocol != None:
			self.protocol.exitThread()
		
		self.socket.close()
		
		if callThreadQuit:
			QtCore.QThread.quit(self)
		
		if self.parent == None:
			sys.exit()


#####################################################################
#####################################################################

class ProtocolHandler(QtCore.QThread):
	
	def __init__(self, log, \
			       serial_device, \
			       mode=DEFAULT_MODE, \
			       DEBUG=DEBUG, \
			       parent=None):
		
		QtCore.QThread.__init__(self,parent)
		
		self.log = log
		self.DEBUG = DEBUG
		self.parent = parent
		
		self.device = None
		self.mode = mode
		
		self.device = serial_device
		
		self.packet_count = 0
		self.bad_packets = 0
		
		self.keep_running = True
		
		self.command_packet = DEFAULT_COMMAND_PACKET
	
	
	##################################################################
	
	def processDataPayload(self, data_payload, payload_timestamp):
		
		packet_update = {}
		packet_update['data_payload'] = data_payload
		packet_update['payload_timestamp'] = payload_timestamp
		
		
		if (self.parent != None):
			self.parent.processPacket(packet_update)
	
	
	##################################################################
	
	def parseStream(self):
		
		# Loop forever, parsing one packet per loop
		packet_count = 0
		
		while self.keep_running:
			
			# Synchronize on [SYNC] bytes
			byte = self.device.read()
			#print byte.encode("hex")
			
			#if (byte != PROTOCOL_SYNC):
			if (byte != PROTOCOL_SYNC_HEAD1):
				continue
			
			byte = self.device.read()
			if (byte != PROTOCOL_SYNC_HEAD2):
				continue
			
			
			payload_timestamp = time.time()
			
			data_payload = self.device.getBuffer()
			data_payload = "%s%s%s" % (PROTOCOL_SYNC_HEAD1, PROTOCOL_SYNC_HEAD2, data_payload)
			
			
			if len(data_payload) < PAYLOAD_MINIMUM_LENGTH:
			#if len(data_payload) != PACKET_LENGTH:
				continue
			
			
			self.processDataPayload(data_payload, payload_timestamp)
			
			
			#if self.DEBUG > 1:
				#packet_count += 1
				#if packet_count >= DEBUG_PACKET_COUNT:
					#print "max debugging count reached, disconnecting"
					#self.keep_running = False
					#self.device.stop()
					#QtCore.QThread.quit(self)
					##sys.exit()
	
	
	##################################################################
	
	def writeStream(self):
		
		# Loop forever, writing one packet per loop
		packet_count = 0
		
		#import cPickle as pickle
		#file = open('packet.data', 'r')
		#packet = pickle.loads(file.read())
		#file.close()
		
		while self.keep_running:
			
			# Preppend or Append [SYNC] bytes
			#if PROTOCOL_ADD_SYNC_TO_HEAD:
				#buffer = PROTOCOL_SYNC_HEAD1
				#buffer += PROTOCOL_SYNC_HEAD2
				#buffer += self.command_packet
			
			#if PROTOCOL_ADD_SYNC_TO_TAIL:
				#buffer = self.command_packet
				#buffer += PROTOCOL_SYNC_HEAD1
				#buffer += PROTOCOL_SYNC_HEAD2
				
			buffer = self.command_packet
			self.device.buffer = buffer
			#self.device.buffer = packet
			#print packet.encode("hex")
			
			# Sleep for 20 ms
			# Based on 50 Hz refresh rate of Blade MLP4DSM RC device
			# (1/50) * 1000 = 20
			QtCore.QThread.msleep(DEVICE_BUFFER_TIMER)
	
	
	##################################################################
	
	def run(self):
		
		self.packet_count = 0
		self.bad_packets = 0
		self.session_start_timestamp = time.time()
		
		if self.mode == 'read':
			self.parseStream()
		
		elif self.mode == 'write':
			self.writeStream()
	
	
	##################################################################
	
	def exitThread(self, callThreadQuit=True):
		
		try:
			self.device.stop()
		except:
			pass
		
		#self.wait()
		if callThreadQuit:
			QtCore.QThread.quit(self)


#####################################################################
#####################################################################

class SerialDevice(QtCore.QThread):
	
	def __init__(self, log, \
			       device_address=SERIAL_DEVICE, \
			       mode=DEFAULT_MODE, \
			       DEBUG=DEBUG, \
			       parent=None):
		
		QtCore.QThread.__init__(self, parent)
		
		self.log = log
		self.DEBUG = DEBUG
		
		self.device_address = device_address
		self.mode = mode
		self.device = None
		self.buffer = ''
		
		if (self.device_address.count(':') == 5):
			# Device address is a Bluetooth MAC address
			self.device = self.initializeBluetoothDevice()
		else:
			# Device address is a serial port address
			self.device = self.initializeSerialDevice()
		
		#self.buffer_check_timer = QtCore.QTimer()
		#QtCore.QObject.connect(self.buffer_check_timer, \
		                       #QtCore.SIGNAL("timeout()"), \
		                       #self.checkBuffer)
		#self.buffer_check_timer.start(DEVICE_BUFFER_TIMER)
		
		self.keep_running = True
	
	
	##################################################################
	
	#def initializeBluetoothDevice(self):
		
		#socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		
		#try:
			#socket.connect((self.device_address, THINKGEAR_DEVICE_BLUETOOTH_CHANNEL))
		
		#except Exception, e:
			#if self.DEBUG:
				#print "ERROR:",
				#print e
				#sys.exit()
		
		
		#return socket
	
	
	###################################################################
	
	def initializeSerialDevice(self):
		
		baudrate = DEFAULT_SERIAL_BAUDRATE
		bytesize = 8
		parity = 'NONE'
		stopbits = 1
		software_flow_control = 'f'
		rts_cts_flow_control = 'f'
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
		
		
		try:
			
			device = serialWrapper(port = self.device_address, \
				                    baudrate = baudrate, \
				                    bytesize = init_byte_size, \
				                    parity = init_parity, \
				                    stopbits = init_stopbits, \
				                    xonxoff = init_software_flow_control, \
				                    rtscts = init_rts_cts_flow_control, \
				                    timeout = timeout)
		
		except Exception, e:
			if self.DEBUG:
				print "ERROR:",
				print e,
				print self.device_address
				sys.exit()
		
		
		#device.flushInput()
		##device.flushOutput()
		
		
		return(device)
	
	
	###################################################################
	
	#def checkBuffer(self):
		
		#if self.DEBUG > 1:
			#print "INFO: Buffer size check:",
			#print len(self.buffer),
			#print "(maximum before reset is %i)" % DEVICE_BUFFER_MAX_SIZE
		
		#if (DEVICE_BUFFER_MAX_SIZE <= len(self.buffer)):
			
			#if self.DEBUG:
				#print "ERROR: Buffer size has grown too large, resetting"
			
			#self.reset()
	
	
	###################################################################
	
	def getBuffer(self):
		
		data_payload = self.buffer
		
		self.resetBuffer()
		
		
		return(data_payload)
	
	
	###################################################################
	
	def resetBuffer(self):
		
		self.buffer = ''
	
	
	###################################################################
	
	def read(self, length=1):
		
		# Sleep for 20 ms if buffer is empty
		# Based on 50 Hz refresh rate of Blade MLP4DSM RC device
		# (1/50) * 1000 = 20
		while len(self.buffer) < length:
			QtCore.QThread.msleep(DEVICE_BUFFER_TIMER)
			
		bytes = self.buffer[:length]
		
		self.buffer = self.buffer[length:]
		
		return(bytes)
	
	
	###################################################################
	
	def stop(self):
		
		#self.buffer_check_timer.stop()
		self.keep_running = False
	
	
	###################################################################
	
	def exitThread(self, callThreadQuit=True):
		
		self.stop()
		self.close()
		
		if callThreadQuit:
			QtCore.QThread.quit(self)
	
	
	###################################################################
	
	def close(self):
		
		self.device.close()
	
	
	###################################################################
	
	def readBuffer(self):
	
		self.buffer = ''
		
		while self.keep_running:
			
			
			# High-Speed Echo Mode
			if (self.DEBUG > 3) and ECHO_ON:
				byte = self.device.recv(PACKET_READ_SIZE)
				self.device.write(byte)
				continue
			
			
			try:
				#byte = self.device.read()
				byte = self.device.recv(PACKET_READ_SIZE)
				
				#if ECHO_ON:
				self.device.write(byte)
				
				if (len(byte) != 0):
					if self.DEBUG > 2:
						print "Device read:",
						print byte,
						if ECHO_ON:
							print byte.encode("hex"),
							print "wrote:",
						print byte.encode("hex")
						
					self.buffer += byte
			
			except:
				if self.DEBUG:
					print "ERROR: failed to read from serial device"
				break
		
		
		self.exitThread()
	
	
	###################################################################
	
	def writeBuffer(self):
	
		self.buffer = ''
		#beacon_timer = 0
		
		while self.keep_running:
			
			if (len(self.buffer) != 0):
				buffer = self.buffer
				self.buffer = ''
				
				
				#if beacon_timer >= 750:
					#buffer += '\xaa' + buffer
					#beacon_timer = 0
				
				
				try:
					self.device.write(buffer)
					
					if self.DEBUG > 1:
						print "Device wrote:",
						#print buffer,
						print buffer.encode("hex")
				
				except:
					if self.DEBUG:
						print "ERROR: failed to write to serial device"
					break
			
			
			# Sleep for 20 ms if buffer is empty
			# Based on 50 Hz refresh rate of Blade MLP4DSM RC device
			# (1/50) * 1000 = 20
			QtCore.QThread.msleep(DEVICE_BUFFER_TIMER)
			#beacon_timer += DEVICE_BUFFER_TIMER
		
		
		self.exitThread()
	
	
	###################################################################
	
	def run(self):
		
		if self.mode == 'read':
			self.readBuffer()
		
		elif self.mode == 'write':
			self.writeBuffer()


#####################################################################
#####################################################################

class serialWrapper(serial.Serial):
	
	#__init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False, interCharTimeout=None)
	
	def recv(self, size=1):
		
		return(self.read(size))


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
	device = SERIAL_DEVICE
	command = DEFAULT_COMMAND
	
	for each in sys.argv:
		
		if each.startswith("--device="):
			device = each[ len("--device="): ]
		elif each.startswith("--command="):
			command = each[ len("--command="): ]
	
	
	app = QtCore.QCoreApplication(sys.argv)
	
	rc = puzzlebox_brainstorms_helicopter_control(device_address=device, command=command, DEBUG=DEBUG)
	
	rc.start()
	
	sys.exit(app.exec_())

