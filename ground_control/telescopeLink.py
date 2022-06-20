"""
telescopeLink.py

Manages serial communication to the DSN
and wireless communication from the telescope.
"""

import socket
import serial
import sys
import time
from PIL import Image
import numpy as np
from cStringIO import StringIO
# import select
# import Queue
import errno

import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import GC_Settings
from DSN import DSN


class TelescopeLink(object):
    """Manages communication with the DSN
    """
    def __init__(self, serialLink):
        self.dsn = DSN(serialLink)

        self.sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_rx.setblocking(0) # Non-blocking mode
        self.sock_rx.bind(('0.0.0.0', GC_Settings.MSG_PORT_RX))

        self.sock_hd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_hd.setblocking(0)
        self.sock_hd.bind(('0.0.0.0', GC_Settings.HIGH_RES_PORT))
        
        self.sock_hd_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock_hd_tcp.setblocking(0)
        self.sock_hd_tcp.bind(('0.0.0.0', GC_Settings.HIGH_RES_PORT))
        self.sock_hd_tcp.listen(1)
        
    def connection(self):
        """Check that the telescope is connected
        """
        name = GC_Settings.TS_NAME
        try:
            GC_Settings.TS_IP = socket.gethostbyname(name)
            print GC_Settings.TS_IP
            return True
        except socket.gaierror as err:
            print "Cannot resolve hostname: ", name, err
            return False

    def send_msg(self, msg):
        """Send a message to the DSN
        """
        self.dsn.send_msg(str(msg))

    def receive_msg(self, msg_buf=64):
        """Receive a text message from the telescope over WiFi
        """
        try:
            data = self.sock_rx.recv(msg_buf)
            return data
        except socket.error as serr:
            # print('No data received')
            return None

    def receive_msg(self):
        """Receive a text message from the telescope over WiFi
        """
        try:
            data, addr = self.sock_rx.recvfrom(1024)
            # print 'TelescopeLink: Found reply'
            # print data
            return data
        except socket.error as serr:
            # print 'TelescopeLink: Did not find any data!'
            return None

    def receive_hd(self, filename):
        '''Receive a HD still image from the telescope

        #sockets from which we except to read
        inputs = [self.sock_hd_tcp]

        #sockets from which we expect to write
        outputs = []
 
        #Outgoing message queues (socket:Queue)
        message_queues = {}
        '''
        t0 = time.time()
        TIMEOUT = 30
        # print 'Opening ', filename
        f = open('images/' + filename, 'wb+')
        file_received = False
        data_begun = False
        num_not_received = 0
        max_missing_thres = 20

        conn, addr = self.sock_hd_tcp.accept()
        # print 'Connection address: ', addr
        while not file_received and not GC_Settings.quit \
                and (time.time() - t0) < TIMEOUT:

            try:
                # data = self.sock_hd.recv(1048576)
                data = conn.recv(131072)
                if not data: 
                    file_received = True
                    break

                # print 'Received message'
                f.write(data)
                data_begun = True
                num_not_received = 0
                if file_received:
                    continue
            except Exception as e:
                # print e
                # print 'Did not find any data!'
                if data_begun:
                    num_not_received += 1
                    if num_not_received > max_missing_thres:
                        # f.close()
                        data_begun = False
                        file_received = True
                        # print('exiting')
            time.sleep(0.001)
            # print 'data_begun', data_begun
            # print 'file_recvd', file_received
            # print 'Waiting for message', time.time() - t0

        f.close()
        if (time.time() - t0) >= TIMEOUT:
            print 'Timed out'
        return file_received

    def receive_hd_array(self, filename):
        """Receive a HD image from the telescope in array format
        """
        t0 = time.time()
        TIMEOUT = 30
        full_buf = ''
        # print 'Opening ', filename
        file_received = False
        data_begun = False
        num_not_received = 0
        max_missing_thres = 20

        while (time.time() - t0) < TIMEOUT and not file_received:
            # print 'Waiting for message'
            try:
                data = self.sock_hd.recv(65536)
                # print 'Data = ', data
                full_buf += data
                # print 'Received message'
                data_begun = True
                num_not_received = 0
                if file_received:
                    continue
            except socket.error as serr:
                # print 'Did not find any data!'
                if data_begun:
                    num_not_received += 1
                    if num_not_received > max_missing_thres:
                        data_begun = False
                        file_received = True
                        # print('exiting')
            time.sleep(0.001)
            # print 'data_begun', data_begun
            # print 'file_recvd', file_received
            
        if (time.time() - t0) > TIMEOUT:
            print 'Timed out'
        else:
            array = np.load(StringIO(full_buf))['frame']
            image = Image.fromarray(array)
            image.save(filename)
        return file_received

    def setup_hex_socket(self):
        """Set up the socket for sending hex programming files
        """
        self.sock_hex = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_hex.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_hex.settimeout(30)

    def send_hex_file(self):
        """Send a hex file for programming
        """
        # file_name = 'main.hex'
        file_name = '../mcu/atmega128/main/debug/main.hex'
        self.setup_hex_socket()  # Must call this or Pi will once send image once
        f = open(file_name, 'rb')
        connected = False
        while not connected:
            try:
                self.sock_hex.connect((GC_Settings.TS_IP,GC_Settings.HEX_PORT))
                connected = True
                print 'Connected'
            except IOError as ioe:
                ecode, _ = ioe.args
                if ecode == errno.EINPROGRESS:
                    print 'Trying to connect'
                else:
                    raise
            
        fullBytes = f.read()
        try:
            #self.sendMsg('$b\n')
            self.sock_hex.sendall(fullBytes)
        except Exception as e:
            print(e)
        #self.sendMsg('$s\n')
        f.close()
        self.sock_hex.close()
        print 'Hex file sent'

    def close(self):
        """Clean up member variables e.g. close sockets
        """
        self.sock_rx.close()
        self.sock_hd.close()
        self.sock_hd_tcp.close()
