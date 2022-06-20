import serial
import struct


if __name__ == "__main__":
	raw = struct.Struct('<hhh')
	floatAngles = struct.Struct('<fff')
	uint8 = struct.Struct('<B')
	ser = serial.Serial("COM6", baudrate=9600)
	while (1):

		if ser.is_open:

			msg = ser.readline()
			if msg[0] == 'r':
				msg = msg[1:7]
				if len(msg) != 6:
					print "Bad packet length: ", len(msg)
				else:
					data = raw.unpack(msg)
					#print "Raw rates: ", data
					mag = (data[0]**2 + data[1]**2 + data[2]**2)**0.5
					print '[%f, %f, %f]' %(data[0]*1.0/mag, data[1]*1.0/mag, data[2]*1.0/mag)


			elif msg[0] == 'f':
				msg = msg[1:((4*3) + 1)]
				if (len(msg) != 4*3):
					print "Bad packet length: ", len(msg)
				else:
					data = floatAngles.unpack(msg)
					print "Angles: ", data	
			elif msg[0] == 'i':
				msg = msg[1:(1 + 1)]
				if (len(msg) != 1):
					print "Bad packet length: ", len(msg)
				else:
					data = uint8.unpack(msg)
					print "Single uint ", data	
			