"""
dataManager.py

Manages incoming and outgoing data formats and validation.
"""

import os
import sys
import time
import datetime
import struct
import errno
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import MSG_Settings


class DataManager(object):

    def __init__(self):
        """Constructor
        """
        # Data to be accessed
        self.msg = None
        self.reply_from_ts = None

        # Flags
        self.msg_ready = False
        self.reply_received = False # Got reply from telescope
        self.readings_received = False # Got telemetry data
        self.status_received = False # Got telescope status
        self.program_ready = False # Ready for wireless program upload

        # Orientation control
        self.ocsIncrement = 1.0
        self.rollIncrement = 5
        self.dc = 0.0 # latest declination command
        self.ra = 0.0 # latest right ascension command

        # Tracks number of image files in different categories
        self.image_files = {"h": 0, "v" : 0}
        self.image_filename = None
        self.image_ready = False # ready to receive an image

        self.image_directory = datetime.datetime.now().strftime(
                "%y-%m-%d-%H-%M-%S")

        # Clean up previous image directories that are empty
        for d in os.listdir("images/"):
            d = "images/" + d
            try:
                os.rmdir(d)
            except OSError as ex:
                if ex.errno == errno.ENOTEMPTY:
                    pass
                    # print "directory not empty"
        # Create a time-specific image directory
        if not os.path.exists(self.image_directory):
            os.makedirs("images/" + self.image_directory)

    def interpret_out(self, msg):
        """Validate and assign a category to an outgoing string message.
        """
        if msg[0] != '$':
            return False
        if msg[1] not in MSG_Settings.GC2TS_FORMAT.keys():
            return False
        ret, key, data = self.valid_format(msg, MSG_Settings.GC2TS_FORMAT)
        if not ret:
            return False
        if msg[1] in self.image_files.keys():
            self.name_image(msg[1])
            self.image_ready = True
        if msg[1] == 'o':
            # Track orientation command angles
            self.dc = float(data[0])
            self.ra = float(data[1])
        if msg[1] == 'g':
            # Special case - wireless MCU programming
            self.program_ready = True
        self.msg = msg
        self.msg_ready = True
        return True

    def interpret_in(self, msg):
        """Validate and assign a category to an incoming string message.

        return 3-tuple meaning "message accepted?, key character, data"
        """
        # Check for correct start and end
        if msg[0] != '$' or msg[-1] != '\n':
            # print 'Invalid message'
            return False, None, None
        if msg[2:4] == 'ok':
            # It is an acknowledgement
            self.reply_from_ts = msg[1:4]
            self.reply_received = True
            return True, None, None
        elif msg[1] not in MSG_Settings.TS2GC_FORMAT.keys():
            # Invalid starting character
            return False, None, None
        # Now validate the rest of the message, i.e. length, values
        ret, key, data = self.valid_format(msg, MSG_Settings.TS2GC_FORMAT)
        if not ret:
            return False, None, None
        if data is None:
            self.status_received = True
            return True, key, data
        # Valid format with some data -> telemetry readings
        self.readings_received = True
        return True, key, data

    def interpret_in_bin(self, msg):
        """Validate and assign a category to an incoming binary message.

        return 3-tuple meaning "message accepted?, key character, data"
        """
        if msg[0] != '$' or msg[-1] != '\n':
            # print 'Invalid message'
            return False, None, None
        if msg[1] == 'w':
            self.reply_received = True
            self.reply_from_ts = msg[2:]
            return True, msg[1], None
        msgLen = len(msg)
        if msgLen == 11:
            byteFormat = struct.Struct('<ccffc')
            _, key, float1, float2, _ = byteFormat.unpack(msg)
            data = [float1, float2]
        elif msgLen == 15:
            byteFormat = struct.Struct('<ccfffc')
            _, key, float1, float2, float3, _ = byteFormat.unpack(msg)
            data = [float1, float2, float3]
        elif msgLen == 5:
            byteFormat = struct.Struct('<ccccc')
            _, key, letter1, letter2, _ = byteFormat.unpack(msg)
            if letter1 == 'o' and letter2 == 'k':
                self.reply_received = True
                self.reply_from_ts = key + letter1 + letter2 + '\n'
                return True, key, None
            else:
                return False, key, None
        elif msgLen == 4:
            byteFormat = struct.Struct('<cccc')
            _, key, char, _ = byteFormat.unpack(msg)
            raw = ord(char)
            data = [raw]
            if type(raw) != int:
                return False, None, None
        elif msgLen == 3:
            byteFormat = struct.Struct('<ccc')
            _, key, _ = byteFormat.unpack(msg)
            data = None
            if key == 's' or key == 'b' or key == 'x' or key == 'y':
                self.status_received = True
                return True, key, data
            return False, key, data
        else:
            return False, None, None
        if key not in MSG_Settings.TS2GC_FORMAT.keys():
            return False, None, None
        #print key, data
        ret, data = self.valid_format_bin(key, data, MSG_Settings.TS2GC_FORMAT)
        if ret:
            self.readings_received = True
            return True, key, data
        return False, None, None
    
    def valid_format(self, msg, formats):
        """Validate msg against the specified formats.

        return 3-tuple meaning "message accepted?, key character, data"
        """
        types = formats[msg[1]][0]
        range_ = formats[msg[1]][1]
        # print types
        # print range_
        params = msg[2:].split(",") # Expect CSV
        # print "DM: Message parameters: ", params
        if types is None:
            # No types to check; message must be fixed length
            return len(msg) == 3, msg[1], None # e.g. "$h\n"
        if len(params) != len(types):
            # Incorrect number of values
            return False, None, None
        data = []
        for i in range(len(params)):
            x = None
            if types is not None:
                # Check types by attempting to cast string
                try:
                    x = types[i](params[i])
                    if types[i] == float:
                        params[i] = "{:.3f}".format(round(x, 3))
                    # if msg[1] == 'w' and i == 1:
                    #     # Link quality percentage
                    #     params[i] = "{:.0f}".format(round(100*x))
                except ValueError:
                    # print "Invalid parameter type"
                    return False, None, None
            if range_ is not None:
                # Check value is within bounds
                if x < range_[0] or x > range_[1]:
                    # print "Invalid parameter value"
                    return False, None, None
            data.append(params[i])
        return True, msg[1], data

    def valid_format_bin(self, key, data, formats):
        """Validate msg against the specified formats.

        return 3-tuple meaning "message accepted?, data"
        """
        types = formats[key][0]
        range_ = formats[key][1]
        if types is None and data is None:
            return True, None
        if len(data) != len(types):
            # print "Invalid parameter count"
            return False, None
        for i in range(len(data)):
            x = None
            if types is not None:
                try:
                    x = types[i](data[i])
                    if types[i] == float:
                        data[i] = "{:.3f}".format(round(x, 3))
                    if key == 'w' and i == 1:
                        # Link quality percentage
                        data[i] = "{:.0f}".format(round(100*x))
                except ValueError:
                    # print "Invalid parameter type"
                    return False, None
            if range_ is not None:
                if x < range_[0] or x > range_[1]:
                    # print "Invalid parameter value"
                    return False, None
        return True, data

    def name_image(self, base):
        """Assign a systematic filename to an incoming image
        """
        self.image_filename = self.image_directory + "/" + base + \
                str(self.image_files[base]) + MSG_Settings.IMAGE_EXT
        self.image_files[base] += 1

    # Below is a set of "pack-down" functions.
    # They might only set one flag, but are defined to be extendable.

    def msg_sent(self):
        self.msg_ready = False

    def reply_printed(self):
        self.reply_received = False

    def image_received(self):
        self.image_ready = False

    def programming_done(self):
        self.program_ready = False

    def readings_printed(self):
        self.readings_received = False

    def status_printed(self):
        self.status_received = False


if __name__ == '__main__':
    dm = DataManager()
    commands = ["o29,-32.3", "p2", "c1", "a0.3,0.2", "m0", "i9,7,23.3",
                "hello", "o29", "o29.3,73.a", "cABC", "m3", "h", "h1"]
    for command in commands:
        print command
        print dm.interpret_out(command)
