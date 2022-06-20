"""
METR4810 
Module for message (e.g. commands and readings) formatting and interpretation on
Raspberry Pi.
"""
# Import primitive modules
import sys
import struct
import os

# Import settings from another directory
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import MSG_Settings


class PiMessageManager(object):
    """
    Class for managing messages.
    """
    def __init__(self, link, dirn):
        """
        Constructor of the class. Store the valid formats for each
        connection from settings.
        :param link: Device to connect to, either 'gc' or 'mcu'
        :param dirn: Data direction, either 'in' or 'out'
        """
        if link == 'gc' and dirn == 'in':  # Inputs from GC
            self.formats = MSG_Settings.GC2TS_FORMAT
        elif link == 'gc' and dirn == 'out':  # Outputs to GC
            self.formats = MSG_Settings.TS2GC_FORMAT
        elif link == 'mcu' and dirn == 'in':  # Inputs from MCU, to be forwarded
            self.formats = {key: MSG_Settings.TS2GC_FORMAT[key]
                            for key in ('r', 'f', 'v', 'b')}
        elif link == 'mcu' and dirn == 'out':  # Outputs to MCU, to be forwarded
            self.formats = {key: MSG_Settings.GC2TS_FORMAT[key]
                            for key in ('o', 'p', 'c', 'm', 'l', 's', 'v', 'm', 'r')}
        else:
            raise ValueError

    def interpretMsg(self, msg):
        """
        Deconstruct a message not in binary form.
        :param msg: Message to be interpreted
        :return: Success state, message type and data associated
        """
        if msg[0] != '$'or msg[-1] != '\n':
            # print 'Invalid message'
            return False, None, None
        if msg[1] not in self.formats.keys():
            # print 'Invalid starting character'
            return False, None, None
        if msg[2:4] == 'ok':
            print('A message was received by GC about 10s ago')
            return True, None, None
        ret, key, data = self.validFormat(msg)
        if not ret:
            return False, None, None
        return True, key, data

    def interpretBinMsg(self, msg):
        """
        Deconstruct a message in pure binary form.
        :param msg: Message to be interpreted
        :return: Success state, message type and data associated
        """
        if msg[0] != '$' or msg[-1] != '\n':
            return False, None, None
        if msg[1] == 'w':
            return True, 'w', msg[2:]
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
        else:
            return False, None, None
        if key not in self.formats.keys():
            return False, None, None
        return True, key, data

    def checkBinMsgLen(self, msg):
        """
        Check if the number of bytes of an entirely binary message is valid.
        :param msg: Message to be verified
        :return: Whether the length is valid and whether the message is a
        reply to a command sent before
        """
        if msg[0] != '$' or msg[-1] != '\n':
            return False, False
        msgLen = len(msg)
        if msg[1] == 'w':
            return True, False
        if msgLen == 5:
            #print 'Got reply from MCU'
            return True, True
        elif msgLen == 11 or msgLen == 15 or msgLen == 3:
            return True, False
        return False, False

    def validFormat(self, msg):
        """
        Validate the format of a message not in binary form.
        :param msg: Message to be validated
        :return: Success state, message type and data associated
        """
        key = msg[1]
        types = self.formats[key][0]
        range_ = self.formats[key][1]
        params = msg[2:].split(',')
        if types is None:  # For messages without data or params
            return len(msg) == 3, key, None
        if len(params) != len(types):
            print 'Invalid parameter count'
            return False, None, None
        data = []
        for i in range(len(params)):
            x = None
            if types is not None:
                try:
                    x = types[i](params[i])
                except ValueError:
                    print 'Invalid parameter type'
                    return False, None, None
            if range_ is not None:
                if x < range_[0] or x > range_[1]:
                    print 'Invalid parameter value'
                    return False, None, None
            if '\n' in params[i]:
                params[i] = params[i][:-1]
            data.append(params[i])
        return True, key, data

    def constructMsg(self, key, data=None):
        """
        Format a message type and the data into one message not in binary form.
        :param key: Message type
        :param data: Data associated with the message type
        :return: The constructed message
        """
        if key not in self.formats.keys():
            # print 'Invalid starting character'
            return '$x\n'
        types = self.formats[key][0]
        msg = '$'+key
        if types is None and data is None:
            return msg+'\n'
        
        range_ = self.formats[key][1]
        data_length = len(data)
        if data_length != len(types):
            print 'Invalid parameter count'
            return '$x\n'
        for i in range(data_length):
            x = None
            if types is not None:
                try:
                    x = types[i](data[i])
                except ValueError:
                    print 'Invalid parameter type'
                    return '$x\n'
            if range_ is not None:
                if x < range_[0] or x > range_[1]:
                    print 'Invalid parameter value'
                    return False
            if i != data_length-1:
                msg += str(x)+','
            else:
                msg += str(x)
        return msg+'\n'

    def constructBinMsg(self, key, data=None):
        """
        Format a message type and the data into one message in pure binary form.
        :param key: Message type
        :param data: Data associated with the message type
        :return: The constructed message
        """
        floatFlag = False
        if key not in self.formats.keys():
            return ''
        stringFormat = '<cc'  # start of line and key placeholder
        types = self.formats[key][0]
        if types is None and data is None:
            stringFormat += 'c'
            singleLetterType = struct.Struct(stringFormat)
            return singleLetterType.pack('$',key,'\n')
        
        range_ = self.formats[key][1]
        data_length = len(data)
        if data_length != len(types):
            return ''

        # Check value and append data type to the format
        for i in range(data_length):
            x = None
            if types is not None:
                try:
                    dataType = types[i]
                    x = dataType(data[i])
                    if range_ is not None:
                        if x < range_[0] or x > range_[1]:
                            return ''
                    
                    if dataType == int:
                        stringFormat += 'c'
                    elif dataType == float:
                        stringFormat += 'f'
                        floatFlag = True
                except ValueError:
                    return ''
        stringFormat += 'c'  # for end of line
        byteFormat = struct.Struct(stringFormat)
        formatLen = len(stringFormat)
        
        if formatLen == 6:  # known message format with 2 floats
            return byteFormat.pack('$', key, types[0](data[0]),
                                   types[1](data[1]), '\n')
        elif formatLen == 7:  # known message format with 3 floats
            return byteFormat.pack('$', key, types[0](data[0]),
                                   types[1](data[1]), types[2](data[2]), '\n')
        elif formatLen == 5:  
            if not floatFlag:
                # known message format with 1 int
                return byteFormat.pack('$', key, chr(types[0](data[0])), '\n')
            else:
                # known message format with 1 float
                return byteFormat.pack('$', key, types[0](data[0]), '\n')
        else:  # Unknown format
            return ''
                
    def replyMsg(self, msg):
        """
        Generate a message as a reply to a command
        :param msg: The command to reply
        :return: The reply message
        """
        return msg[0:2]+'ok\n'
