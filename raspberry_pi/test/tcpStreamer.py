import socket
import time
import picamera


camera = picamera.PiCamera(resolution=(1920, 1080))
camera.framerate = 5
camera.exposure_mode = 'sports'
camera.video_stabilization = True
time.sleep(2)
found = False

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
while not found:
    try:
        host = socket.gethostbyname('HR-2017-PC7I')
	found = True
    except socket.gaierror, err:
        print "cannot resolve hostname: ", name
        time.sleep(1)

client_socket = socket.socket()
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.settimeout(10)
client_socket.connect((host, 7000))
print('connected')

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    # Start a preview and let the camera warm up for 2 seconds
    #camera.start_preview()
    camera.start_recording(connection, format='h264', bitrate=19000000)
    while True:
        time.sleep(1)
finally:
    connection.close()
    client_socket.close()
    camera.close()
