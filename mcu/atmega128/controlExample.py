import socket
import struct
import numpy as np
import time

UNITY_IP = 'localhost'
UNITY_PORT = 8001
BUFFER_SIZE = 1024

X, Y, Z = 0,1,2

def anglesToXYZ(angles):
	vector = np.array([0,0,0], dtype=float)
	angles = np.deg2rad(angles.astype(float))
	vector[X] = np.cos(angles[Y]) * np.cos(angles[Z])
	vector[Y] = np.cos(angles[Y]) * np.sin(angles[Z])
	vector[Z] = -np.sin(angles[Y])
	return vector

def anglesToRotationMatrix(angles):
	angles = np.deg2rad(angles.astype(float))
	x = angles[X]
	y = angles[Y]
	z = angles[Z]

	Rx = np.array([[1, 			0,			0],
				   [0, 			np.cos(x), 	-np.sin(x)],
				   [0, 			np.sin(x), 	np.cos(x)]])


	Ry = np.array([[np.cos(y), 	0,			np.sin(y)],
				   [0, 			1, 			0],
				   [-np.sin(y),	0,	 		np.cos(y)]])

	Rz = np.array([[np.cos(z), 	-np.sin(z),	0],
				   [np.sin(z), 	np.cos(z), 	0],
				   [0,			0,	 		1]])

	R = np.matmul(np.matmul(Rz, Ry), Rx)
	#R = np.matmul(Rx, np.matmul(Rz, Ry)) # this order is probably not right
	print R
	return np.linalg.inv(R)

def generate_torque_vector(currentAngles, desiredAngles):
	currentPoseVector = anglesToXYZ(currentAngles)
	desiredPoseVector = anglesToXYZ(desiredAngles)
	print currentPoseVector
	print desiredPoseVector

	torqueVectorWorld = np.cross(currentPoseVector, desiredPoseVector)
	print "World: ",  torqueVectorWorld
	R = anglesToRotationMatrix(currentAngles)
	torqueVectorTelescope = np.matmul(R, torqueVectorWorld)
	print "Telescope: ",  torqueVectorTelescope
	return torqueVectorTelescope

if __name__ == "__main__":
	currentAngles = np.array([45, 45, 0])
	desiredAngles = np.array([0, -45, -45])

	torque = generate_torque_vector(currentAngles, desiredAngles)
	UNITY = 1
	if UNITY:
		unitySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		unitySocket.bind((UNITY_IP, UNITY_PORT))
		unitySocket.listen(1)
		print "Waiting for unity"
		unityConnection, addr = unitySocket.accept()
		print "Unity connected!"

		while(1):
			sendData = "METR%f,%f,%f,%f,%f,%f,%f,%f,%f" % (
						float(currentAngles[X]), float(currentAngles[Y]), float(currentAngles[Z]), 
						float(desiredAngles[X]), float(desiredAngles[Y]), float(desiredAngles[Z]), 
						torque[X], torque[Y], -torque[Z])
			unityConnection.send(sendData)

		unityConnection.close()
		unitySocket.close()