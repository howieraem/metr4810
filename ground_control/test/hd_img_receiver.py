import socket
import os
import time
import sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 7001))
server_socket.setblocking(0)
f = open('test1.jpeg','wb+')
file_received = False
data_begun = False
num_not_received = 0
max_missing_thres = 10
while not file_received:
    #print "Waiting for message"
    try:
        data = server_socket.recv(4096000)
        #print "Received message"
        f.write(data)
        data_begun = True
        num_not_received = 0
        if file_received:
            continue
    except Exception as e:
        print(e)
        print "Did not find any data!"
        if data_begun:
            num_not_received += 1
            if num_not_received > max_missing_thres:
                f.close()
                data_begun = False
                server_socket.close()
                file_received = True
                print('exiting')
    time.sleep(0.001)
    print 'data_begun',data_begun
    print 'file_recvd',file_received


