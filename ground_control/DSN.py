"""
DSN.py

Writes messages to the DSN via a serial connection.
"""
import time

class DSN(object):
    def __init__(self, serialLink):
        self.serialLink = serialLink

    def send_msg(self, msg):
        print "DSN: writing to serial"
        # time.sleep(10) # simulate delay
        self.serialLink.write(msg)
