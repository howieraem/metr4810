"""
transmitter.py

Manages communication out from the DSN and to the telescope.
"""

import sys
import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import GC_Settings
import socket


class Transmitter(object):

    def __init__(self, serialLink):
        self.serialLink = serialLink
        self.sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_tx.setblocking(0)

    def send_if_ready(self):
        """Send a message if there is one waiting on the serial port
        """
        if self.serialLink.inWaiting() > 0:
            self.read_and_send_msg()

    def send_msg(self, msg):
        """Send a message to the telescope
        """
        print "Transmitter: Sending message"
        try:
            self.sock_tx.sendto(msg, (GC_Settings.TS_IP, 
                    GC_Settings.MSG_PORT_TX))
            print "Transmitter: Sent message"
        except socket.error as serr:
            print "Transmitter: Could not dispose of data!"
            return None

    def read_and_send_msg(self):
        """Read a message from the serial port (DSN). 

        Currently assumes messages are new line terminated.
        """
        if self.serialLink.is_open:
            try:
                print "Transmitter: Reading message"
                msg = self.serialLink.readline()
                print "Transmitter: Read message: ", msg
                self.send_msg(msg)
                return msg
            except Exception as e:
                print e
                return None
        else:
            print "DSN: Serial port is no longer open!"
        return None
