import socket
import sys
import time

import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import GC_Settings

sock_hex = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_hex.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock_hex.settimeout(30)

file_name = 'main.hex'

f = open(file_name, 'rb')
connected = False
while not connected:
    try:
        sock_hex.connect((GC_Settings.TS_IP,GC_Settings.HEX_PORT))
        connected = True
        print 'Connected'
    except IOError as ioe:
        ecode, _ = ioe.args
        if ecode == errno.EINPROGRESS:
            print 'Trying to connect'
        else:
            raise

#time.sleep(1)    
fullBytes = f.read()
try:
    #sendMsg('$b\n')
    sock_hex.sendall(fullBytes)
except Exception as e:
    print(e)
f.close()
sock_hex.close()
print 'Hex file sent'
