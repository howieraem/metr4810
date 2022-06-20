import socket
import time

UDP_IP = "192.168.43.26"
UDP_PORT = 8000
MESSAGE = "p%f,%f" % (1322.2451, 2321.59)

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    time.sleep(0.5)
