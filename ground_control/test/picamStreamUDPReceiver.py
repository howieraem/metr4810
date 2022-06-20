'''
        Script for video stream UDP receiver. Requires VLC installed and added to PATH
'''
import socket
import subprocess
import numpy as np
import cv2

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 8000))

try:
    # Run a viewer with an appropriate command line.
    #cap = cv2.VideoCapture()
    cmdline = ['vlc', '--demux', 'mjpeg', '-']
    player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    while True:
        # Repeatedly read up to 32k of data from the connection and write it
        # to the media player's stdin; Use a large buffer to avoid truncating 
        # UDP messages
        #cap.open("rtp://192.168.43.26:8000")
        #print(cap.isOpened())
        data = server_socket.recv(65536)
        if not data:
                break
        #print(data)
        player.stdin.write(data)
finally:
    server_socket.close()
    #player.terminate()
