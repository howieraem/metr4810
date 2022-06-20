import time
import serial
import struct

messageType = struct.Struct('<ccfffc')
ser = serial.Serial("COM7", baudrate=115200)
orientationFormat = struct.Struct('<ccffc')	
STX = '$'
ETX = '\n'
while 1:
	if ser.is_open:
		#msg = ser.readline()
		orientationFormat.pack(STX, 'o', declination, rightA, '\n')
		msg = messageType.pack('$', 'f', 1.0,2.0,3.0, '\n')
		print msg
		ser.write(msg)
		time.sleep(1)
		msg = messageType.pack('$', 'f', 55.0,2.0,3.0, '\n')
		print msg
		ser.write(msg)
		time.sleep(1)
		