"""
dummySerial.py

For testing with no serial, without modifying DSN code
"""

class DummySerial(object):

    def __init__(self):
        self.is_open = True
        self.msg = ""

    def write(self, msg):
        print "DummySerial: writing message ", msg
        self.msg = msg

    def readline(self):
        print "DummySerial: reading message ", self.msg
        msg = self.msg
        self.msg = ""
        return msg

    def inWaiting(self):
        """Transmitter calls to check if a message is waiting
        """
        return len(self.msg) > 0
