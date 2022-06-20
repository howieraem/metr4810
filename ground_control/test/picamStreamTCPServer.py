'''
	Script for video stream TCP server. Requires VLC installed and added to PATH
'''
import socket
import subprocess

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 7000))
server_socket.listen(0)
connection = server_socket.accept()[0].makefile('rb')
try:
    # Run a viewer with an appropriate command line.
	cmdline = ['vlc', '--demux', 'h264', '-']
	player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
	while True:
		# Repeatedly read 4kB of data from the connection and write it to
		# the media player's stdin (buffering)
		data = connection.read(8192)
		if not data:
			break
		player.stdin.write(data)
finally:
	connection.close()
	server_socket.close()
	player.terminate()
