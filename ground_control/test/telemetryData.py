import socket
import time
import random

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

t0 = time.time()
while True:
    data = [str(round(1000*random.random(), 4)) for i in range(20)]
    data[10] = str(round(150000*random.random(), 5))
    messages = [
        "$r" + data[0] + "," + data[1]+ "," + data[2] + "\n",
        "$f" + data[3] + "," + data[4]+ "," + data[5] + "\n",
        "$v" + data[6]+ "," + data[7] + "\n",
        "$w" + data[8]+ "," + data[9]+ "," + data[10] + "\n"
    ]
    print "Sending data"
    try:
        for msg in messages:
            sock_tx.sendto(msg, (UDP_IP_TX, UDP_PORT_TX))
        print "Sent data"
    except Exception:
        print "Could not dispose of data!"
    time.sleep(1)
