import socket
import struct
import numpy
import time

UNITY_IP = 'localhost'
UNITY_PORT = 8001
BUFFER_SIZE = 1024

unitySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
unitySocket.bind((UNITY_IP, UNITY_PORT))
unitySocket.listen(1)
print "Waiting for unity"
unityConnection, addr = unitySocket.accept()
print "Unity connected!"

import serial
import struct

X,Y,Z = 0,1,2

floatAngles = struct.Struct('<fff')
ser = serial.Serial("COM7", baudrate=9600)
			
TARGET = [0, 20, -10];
SEND_TARGET = True

#logFile = open("bothLog.csv", "w")
#logFile.write("Gyro X, Gyro Y, Gyro Z, Mag X, Mag Y, Mag Z\n")
while 1:
	if ser.is_open:
		msg = ser.readline()
		if msg[0] != '$':
			print "First character not $, %c instead\n" % (msg[0])
		if msg[1] == 'r':
			msg = msg[2:((4*3) + 2)]
			if (len(msg) != 4*3):
				print "Bad packet length: ", len(msg)
			else:
				data = floatAngles.unpack(msg)
				sendData = "METR%f,%f,%f" % (-float(data[0]), -float(data[1]), float(data[2]))
				print "Angles: ", data	
				unityConnection.send(sendData)

unityConnection.close()
unitySocket.close()


