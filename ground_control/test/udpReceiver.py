import socket
import time

UDP_IP_RX = ""
UDP_PORT_RX = 8000
UDP_IP_TX = "127.0.0.1"
UDP_PORT_TX = 8001

sock_rx = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock_rx.setblocking(0)
sock_rx.bind((UDP_IP_RX, UDP_PORT_RX))
sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_tx.setblocking(0)

while True:
    print "Waiting for message"
    try:
        data, addr = sock_rx.recvfrom(1024) # buffer size is 1024 bytes
        print "Received message:", data
        try:
            if data == '$h':
                sock_tx.sendto("Pi: hok\n", (UDP_IP_TX, UDP_PORT_TX))
            if data[1] == 'o':
                sock_tx.sendto("Pi: ook\n", (UDP_IP_TX, UDP_PORT_TX))
        except Exception:
            print "Could not dispose of data!"
    except Exception:
        print "Did not find any data!"

    time.sleep(1)
