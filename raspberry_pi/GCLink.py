"""
METR4810 
Module for network connection to ground control on Raspberry Pi.
"""
# Import primitive modules
import socket
import sys
import time
from PIL import Image
import numpy as np
from PiMessageManager import PiMessageManager
import errno
import os

# Import settings from another directory
sys.path.append(os.path.abspath('..//')) 
from conf.settings import TS_Settings


class GCLink(object):
    """
    Class for ground control connection.
    """
    def __init__(self):
        """
        Constructor of the class. Initialise the UDP sockets.
        """
        self.getGCIP()  # Blocking until ground control host is found
        self.sock_msg_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_msg_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_hd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.sock_msg_tx.setblocking(0)
        self.sock_msg_rx.setblocking(0)
        self.sock_hd.setblocking(0)

        self.sock_msg_rx.bind(('0.0.0.0', TS_Settings.MSG_PORT_RX))

        self.msg_in_manager = PiMessageManager('gc', 'in')
        self.msg_out_manager = PiMessageManager('gc', 'out')

        self.setupImgTCP()
        self.stream_conn = None
        
    def getGCIP(self):
        """
        Retrieves the IP address from the hostname of the ground control.
        :return
        """
        while TS_Settings.GC_IP is None:
            try:
                TS_Settings.GC_IP = socket.gethostbyname(TS_Settings.GC_NAME)
            except socket.gaierror:
                time.sleep(1)  # Ground control host is unavailable yet

    def setupImgTCP(self):
        """
        Reset the TCP socket for still high-resolution images.
        :return
        """
        self.sock_hd_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock_hd_tcp.setblocking(0)
        self.sock_hd_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_hd_tcp.settimeout(30)

    def connectStreamSocket(self):
        """
        Connect the TCP socket for video streaming.
        :return
        """
        self.sock_stream = socket.socket()
        self.sock_stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_stream.settimeout(30)
        self.sock_stream.connect((TS_Settings.GC_IP, TS_Settings.STREAM_PORT))
        print('Video streaming socket connected')
        self.stream_conn = self.sock_stream.makefile('wb')

    def setupHexSocket(self):
        """
        Reset the TCP socket for *.hex MCU programming files
        :return
        """
        self.sock_hex = socket.socket()
        self.sock_hex.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_hex.settimeout(30)
        self.sock_hex.bind(('0.0.0.0', TS_Settings.HEX_PORT))

    def receiveHexFile(self):
        """
        Receive and save the *.hex MCU programming file from the ground control.
        :return
        """
        tot_fail = 300
        num_fail = 0
        self.setupHexSocket()
        self.sock_hex.listen(1)
        conn, addr = self.sock_hex.accept()
        print 'Hex file transfer ready'
        f = open('main.hex', 'wb+')
        try:
            while num_fail <= tot_fail:
                l = conn.recv(4096)
                if not l:
                    num_fail += 1
                    time.sleep(0.01)
                else:
                    print 'Receiving hex file'
                    f.write(l)
                    num_fail = 0
        finally:
            f.close()
            conn.close()
            self.sock_hex.close()

    def sendMsg(self, msg):
        """
        Send string messages to the ground control via the messaging UDP socket.
        :param msg: Message to be sent
        :return
        """
        self.sock_msg_tx.sendto(msg, (TS_Settings.GC_IP,
                                      TS_Settings.MSG_PORT_TX))

    def receiveMsg(self,
                   msg_buf=64):
        """
        Read messages of some buffer size from the messaging UDP socket.
        :param msg_buf: Buffer size to read
        :return: The string received
        """
        data = self.sock_msg_rx.recv(msg_buf)
        return data

    def receiveReply(self):
        """
        Read messages from ground and reply to valid messages.
        :return: The message key and any data associated.
        """
        msg = self.receiveMsg()
        if msg is not None:
            ret, key, data = self.msg_in_manager.interpretMsg(msg)
            if ret and key is not None:
                reply = self.msg_in_manager.replyMsg(msg)
                self.sendMsg(reply)
                return key, data
        return None, None

    def sendHDTCPOnce(self, file_name):
        """
        Transmit still image files over the TCP socket.
        :param file_name: Name of the image in the file system
        :return
        """
        self.setupImgTCP()  # Must call this or RPi will only send image once
        f = open(file_name, 'rb')
        connected = False
        while not connected:
            try:
                self.sock_hd_tcp.connect((TS_Settings.GC_IP,
                                          TS_Settings.HIGH_RES_PORT))
                connected = True
                print 'Connected'
            except IOError as ioe:
                ecode, _ = ioe.args
                if ecode == errno.EINPROGRESS:
                    print 'Trying to connect'
                else:
                    raise
            
        fullBytes = f.read()  # Load the image into memory
        try:
            self.sendMsg('$b\n')  # RPi in busy state
            self.sock_hd_tcp.sendall(fullBytes)
        except Exception as e:
            print(e)
        self.sendMsg('$s\n')  # RPi done with transmission
        f.close()
        self.sock_hd_tcp.close()
        print 'Img sent'

    def sendValidMsg(self, key, data):
        """
        Send a valid formatted message to the ground.
        :param key: Type of message
        :param data: Data associated with message type
        :return
        """
        msg = self.msg_out_manager.constructMsg(key, data)
        self.sendMsg(msg)
        
    def terminate(self):
        """
        Free the memory once the main program terminates.
        :return
        """
        if self.stream_conn is not None:
            self.stream_conn.close()
        self.sock_msg_tx.close()
        self.sock_msg_rx.close()
        self.sock_stream.close()
        self.sock_hd.close()
        self.sock_hd_tcp.close()
