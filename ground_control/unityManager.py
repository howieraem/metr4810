"""
unityManager.py

Manages the interface with the telescope simulation in Unity.
"""

import sys
import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import GC_Settings
import socket

class UnityManager(object):
    
    def __init__(self):
        self.unitySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.unitySocket.bind((GC_Settings.UNITY_IP, GC_Settings.UNITY_PORT))
        self.unitySocket.listen(1)
        print "Waiting for unity"
        self.unityConnection, addr = self.unitySocket.accept()
        print "Unity connected!"

    def send(self, key, data):
        if key == 'r':
            sendData = "METR%f,%f,%f" % (
                    -float(data[0]), -float(data[1]), float(data[2]))
            self.unityConnection.send(sendData)

