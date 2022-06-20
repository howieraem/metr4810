"""
METR4810 
Module for general purpose IO ports on Raspberry Pi communicating with the MCU.
"""
# Import primitive modules
import serial
import time
import sys
import RPi.GPIO as GPIO
import subprocess as sp
from PiMessageManager import PiMessageManager
import os

# Import settings from another directory
sys.path.append(os.path.abspath('..//'))
from conf.settings import TS_Settings


class MCULink(object):
    """
    Class for MCU connection.
    """
    def __init__(self,
                 baudrate=TS_Settings.BAUDRATE,
                 timeout=TS_Settings.TIMEOUT):
        """
        Constructor of the class. Using serial0 device for UART.
        :param baudrate
        :param timeout
        """
        self.port = serial.Serial('/dev/serial0',
                                  baudrate=baudrate,
                                  timeout=timeout)
        self.msg_in_manager = PiMessageManager('mcu', 'in')
        self.msg_out_manager = PiMessageManager('mcu', 'out')
        self.enabled = self.port.is_open
        if not self.enabled:
            self.openLink()
        GPIO.setmode(GPIO.BOARD)  # Refer to physical pin 1 rather than BCM

    def sendMsg(self, msg):
        """
        Send a string over UART.
        :param msg: Message to be sent
        :return
        """
        if self.enabled:
            self.port.write(msg)

    def readMsg(self):
        """
        Read a string with an end of line character from the UART buffer.
        :return: The message read
        """
        if self.enabled:
            msg = self.port.readline()
        return msg

    def readBin(self):
        """
        Read a valid binary message from MCU.
        :return: Whether reading is successful, whether message is a reply to a
        command sent to MCU before, and the actual message content
        """
        msg = self.readMsg()
        if msg == '':
            return False, False, None
        ret, commandFlag = self.msg_in_manager.checkBinMsgLen(msg)
        if ret:
            if msg[1] == 'y':
                print 'OCS is ready for taking image'
            '''
            elif msg[1] == 'w':
                print 'got mcu debug msg'
            '''
            return True, commandFlag, msg    
        return False, False, None

    def sendValidMsg(self, key, data):
        """
        Send a valid formatted string to MCU with data not in binary form.
        :param key: Message type
        :param data: Data associated with message type
        :return
        """
        msg = self.msg_out_manager.constructMsg(key, data)
        self.sendReply(msg)

    def sendValidBinMsg(self, key, data):
        """
        Send a valid formatted string to MCU with data purely in binary form.
        :param key: Message type
        :param data: Data associated with message type
        :return
        """
        msg = self.msg_out_manager.constructBinMsg(key, data)
        self.sendMsg(msg)

    def openLink(self):
        """
        Open the UART port.
        :return
        """
        if not self.enabled:
            self.port.open()
            self.enabled = True

    def terminate(self):
        """
        Free the memory once the main program exits.
        :return
        """
        self.port.close()
        self.enabled = False

    def setPinHigh(self, pin_num):
        """
        Set a GPIO pin high.
        :param pin_num: Physical (not BCM) pin number
        :return
        """
        GPIO.setup(pin_num, GPIO.OUT)
        GPIO.output(pin_num, GPIO.HIGH)

    def setPinLow(self, pin_num):
        """
        Set a GPIO pin low.
        :param pin_num: Physical (not BCM) pin number
        :return
        """
        GPIO.setup(pin_num, GPIO.OUT)
        GPIO.output(pin_num, GPIO.LOW)
        
    def setPinInput(self, pin_num):
        """
        Set a GPIO pin as input.
        :param pin_num: Physical (not BCM) pin number
        :return
        """
        GPIO.setup(pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
    def readPinInput(self, pin_num):
        """
        Read the state of a GPIO pin.
        :param pin_num: Physical (not BCM) pin number
        :return
        """
        self.setPinInput(pin_num)
        return GPIO.input(pin_num)
        
    def checkPowerCycle(self):
        """
        An alternative to the power cycling of imaging and telemetry which
        reads the state of a pin connected to MCU and if high reboots the RPi
        :return
        """
        if self.readPinInput(TS_Settings.POWER_CYCLE_PIN):
            os.system('sudo reboot')

    def truncateMsgIn(self):
        """
        Clean any message left in the UART buffer.
        :return
        """
        self.port.reset_input_buffer()

    def programMCU(self):
        """
        Remote programming of the MCU via UART/SPI shared pins.
        :return
        """
        self.port.close()  # Close UART communication first
        hexScript = 'programHex.sh'
        p = sp.call(hexScript, stdout=sp.PIPE)
        print p.communicate()[0]
        time.sleep(0.5)
        self.port.open()  # Reopen UART communication
