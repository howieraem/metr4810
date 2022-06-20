"""
METR4810 
File for constant configurations

Usage:

import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from config.settings.FooSettings import *
"""
import numpy as np

class MSG_Settings(object):
    """
    Message formats.
    """
    GC2TS_FORMAT = {
        'o': [[float, float], [-360.0, 360.0]], # orientation
        'p': [[int], [0, 3]], # power cycle
        'c': [[float, float, float], [-360.0, 360.0]], # manual calibrate
        'r': [[float], [-360.0, 360.0]], # calibrate roll only
        'm': [[float, float, float], None], # overwrite roll gyro readings
        'l': [[int], [0, 7]], # debug led pattern
        'i': [[int, int], None], # camera parameters
        'h': [None, None], # capture a hi-res image
        't': [None, None], # test for response
        'g': [None, None], # wireless mcu programming
        's': [[int], [0, 100]], # manage OCS
        'v': [[int], [0, 1]], # request electrical readings
        'w': [None, None]
    }

    TS2GC_FORMAT = {
        'r': [[float, float, float], None],  # gyro readings
        'f': [[float, float, float], None],  # magnetometer readings
        'v': [[float, float], None],  # electrical readings
        'w': [str, None],  # debugging msu message
        's': [None, None],  # file transmission done
        'b': [None, None],  # pi/mcu busy
        'x': [None, None],  # bad message indicator
        'y': [None, None]  # OCS indicates good to take pic
    }

    IMAGE_EXT = ".jpeg"

class TS_Settings(object):
    """
    Satellite settings.
    """
    GC_NAME = 'HL-LAPTOP'
    GC_IP = None  # Change this to GC's actual IP
    MSG_PORT_TX = 9001  # Corresponds to RX on GC
    MSG_PORT_RX = 9000  # Corresponds to TX on GC
    STREAM_PORT = 7000  # Real-time video streaming
    HEX_PORT = 6000  # Wireless MCU programming
    HIGH_RES_PORT = 5000  # High-resolution image/video
    HEX_PORT = 6000  # Wireless MCU programming
    BAUDRATE = 9600  # UART transmission rate
    TIMEOUT = 0.5  # Maximum time to hang while reading or writing data
    POWER_CYCLE_PIN = 7  # Received pin signal from MCU to reboot

class GC_Settings(object):
    """
    Ground control settings.
    """
    TS_IP = '192.168.77.1' # '192.168.137.102'  # Change this to RPi's actual IP
    UNITY_IP = '127.0.0.1'
    MSG_PORT_RX = TS_Settings.MSG_PORT_TX
    MSG_PORT_TX = TS_Settings.MSG_PORT_RX
    STREAM_PORT = TS_Settings.STREAM_PORT # Real-time video streaming
    HIGH_RES_PORT = TS_Settings.HIGH_RES_PORT  # High-resolution image/video
    HEX_PORT = TS_Settings.HEX_PORT
    UNITY_PORT = 8001
    TCP_STREAM_ADDR = 'tcp://0.0.0.0:' + str(STREAM_PORT) \
            + '?listen=1?recv_buffer_size=8192'
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080

    USE_DSN = False  # Disable serial communication for testing without it
    DSN_PORT = "COM4"
    DSN_BAUD = 1200

    MSG_TIMEOUT = 10  # After this many seconds with no telescope status
                      # whatsoever, assume the telescope is ready

    quit = False # Flag for closing threads (modifiable)


class CAM_Settings(object):
    """
    Raspberry Pi camera settings.
    """
    FULL_RES = (3280, 2464)   # High-resolution still image resolution
    VIDEO_WIDTH = GC_Settings.VIDEO_WIDTH  # Video width of live stream
    VIDEO_HEIGHT = GC_Settings.VIDEO_HEIGHT  # Video height of live stream
    FULL_FRAMERATE = 9  # Maximum frame rate of the camera sensor
    ROTATION = 0  # Angle to rotate the frame due to mechanical mounting
    EXPOSURE_MODE = 'sports'  # Exposure calculation mode
    EXPOSURE_COMPENSATION = 25  # Offset of exposure
    ISO = 0  # Zero means automatic ISO calculation
    SHUTTER_SPEED = 0   # Zero means automatic shutter speed calculation
    DYNAMIC_RANGE = 'high'  # Dynamic range
    WHITE_BAL_MODE = 'cloudy'  # White balance calculation mode
    METER_MODE = 'backlit'  # Exposure sampling mode
    SHARPNESS = 100  # Sharpness pre-processing
    SATURATION = -40  # Saturation pre-processing, 0 is unchanged
    BRIGHTNESS = 50  # Brightness pre-processing, 50 is unchanged
    CONTRAST = 0  # Contrast pre-processing, 0 is unchanged
    STABILIZATION = True  # Video stabilization mode
    IMAGE_EFFECT = 'denoise'  # Image effect pre-processing
    VID_ENCODING = 'mjpeg'  # Video stream format
    ENCODE_BITRATE = 17000000  # Video encoding bit rate
    QUALITY = 85  # Video quality
    ARRAY_ENCODING = 'bgr'  # Format of continuous capture
    MULTICAST_DELAY = 0.1   # Necessary delay time for capturing images in
                            # addition to an existing video streaming task
    IMG_FILE_ENCODING = MSG_Settings.IMAGE_EXT[1:]  # Image file backend
    WARM_UP_TIME = 2  # Time to wait when camera is accommodating to lighting
    WIDTH = 320    # Image width of continuous capture
    HEIGHT = 240   # Image height of continuous capture
