"""
METR4810 
Main program loop on Raspberry Pi communicating with ground, MCU and camera.
"""
# Import modules
#-------------------------------------------------------------------------------
# Primitive modules
import time
import socket
import picamera
import errno
import serial
from threading import Thread

# Custom modules
from GCLink import GCLink
from CameraLink import CameraLink
from MCULink import MCULink


# Multithreading functions and global variables
#-------------------------------------------------------------------------------
readyFlag = False
camEnableFlag = False
camBusyFlag = False
execFlag = True
mcuCommandSuccess = False
mcuCommandTimeout = 5
cam = None

def gcTX(gcl, mcul, cam):
    """
    Receives messages from MCU and forwards to ground
    :param gcl: Ground control link object
    :param mcul: MCU link object
    :param cam: Camera object
    :return: None
    """
    global mcuCommandSuccess, camEnableFlag, camBusyFlag
    mcul.truncateMsgIn()  # Flush the input buffer on start
    while True:
        try:
            ret, mcuCommandSuccess, msg = mcul.readBin()
            if ret and msg is not None:
                gcl.sendMsg(msg)
                '''
                if camEnableFlag and msg == '$y\n' and not camBusyFlag:
                    camBusyFlag = True
                    time.sleep(0.1)
                    cam.captureStillImageFile('test')
                    time.sleep(0.05)
                    gcl.sendHDTCPOnce('test.jpeg')
                    camBusyFlag = False
                    mcul.truncateMsgIn()
                '''
            time.sleep(0.01)
        except KeyboardInterrupt:
            print 'Task cancelled by user'
            break
        except socket.error as soerr:
            print(soerr)
            pass  # Non-blocking socket without data throws exceptions
        except serial.SerialException as seerr:
            print 'Serial communication error'
        except Exception as e:
            print(e)  # Unexpected error

# Start the whole algorithm once the test command is received
def getReady(gcl):
    """
    Wait for ground instructions before executing main loop.
    :param gcl: Ground control link object
    :return: None
    """
    global readyFlag
    try:
        key, data = gcl.receiveReply()
        print 'Received GC msg: ', key, data
        if key == 't':
            readyFlag = True
    except socket.error:
        time.sleep(0.1)
        pass  # Non-blocking socket without data throws exceptions
    except KeyboardInterrupt:
        print 'Task cancelled by user'

# Initializations of hardware and the corresponding module
#-------------------------------------------------------------------------------
try:
    gcl = GCLink()  # Blocking until connection is established
    print 'Ground control Link initialised'

    # Wait for ground control instruction before proceeding
    while not readyFlag:
        getReady(gcl)

    mcul = MCULink()
    print 'MCU Link initialised'
    
    cam = CameraLink()
    print 'Camera initialised'
    camEnableFlag = True
except picamera.PiCameraError as cerr:
    print(cerr)  # Camera connection error, not enabling camera functions
except socket.timeout:
    print('Cannot connect to ground control')
print 'Initialisations done'

# Set up threads other than the main thread
#-------------------------------------------------------------------------------
if camEnableFlag:
    """
    Record a video stream to the network.
    """
    tv = Thread(target=cam.recordVideoStream, args=(gcl,))
    tv.daemon = True
    tv.start()

"""
Receives MCU messages and forwards to ground.
"""
tm = Thread(target=gcTX, args=(gcl, mcul, cam))
tm.daemon = True
tm.start()

# Main thread loop
#-------------------------------------------------------------------------------
while True:
    """
    The main thread receives commands from the ground, and executes camera 
    operations or forwards to the MCU
    """
    try:
        key, data = gcl.receiveReply()
        print 'Received GC msg: ', key, data
        if key == 'h' and camEnableFlag and not camBusyFlag:
            # Take a high-resolution still image
            camBusyFlag = True
            cam.captureStillImageFile('test')
            time.sleep(0.05)
            gcl.sendHDTCPOnce('test.jpeg')
            camBusyFlag = False
        elif key == 'i':
            # Adjust the camera exposure and ISO
            cam.setShutter(exposure_compensation=int(data[0]), iso=int(data[1]))
        elif key in mcul.msg_out_manager.formats and data is not None:
            # Receive commands for the MCU and forward them to there.
            mcul.sendValidBinMsg(key, data)
            startTime = time.time()
            while time.time() <= (startTime + mcuCommandTimeout) \
                and not mcuCommandSuccess:
                time.sleep(0.01)  # Wait for reply from MCU
            if time.time() >= startTime + mcuCommandTimeout:
                print 'MCU reply timed out'
        time.sleep(0.01)

    except KeyboardInterrupt:
        print 'Execution cancelled by user'
        execFlag = False
    except picamera.PiCameraError as cerr:
        print(cerr)
        camEnableFlag = False
        execFlag = False
    except socket.error as soerr:
        if soerr.errno == errno.ECONNRESET:
            gcl.sock_hd_tcp.close()
            errmsg = 'Image socket connection dropped, retry the h command link.'
            gcl.sendMsg('$w'+msg+'\n')
        time.sleep(0.01)
        pass  # Non-blocking socket without data throws exceptions
    except IOError as ioe:
        # Potential errors for TCP sockets
        code, msg = ioe.args
        if code == errno.EINPROGRESS:
            print 'Trying to connect'
            pass
        elif code == errno.EPIPE:
            print 'TCP non-blocking connection dropped, reconnecting'
            gcl.connectStreamSocket()
            pass
        else:
            execFlag = False
            print(ioe)  # Unexpected error
    except serial.SerialException:
        print 'Serial communication error'
        execFlag = False
    except Exception as e:
        print(e)
        pass  # Unexpected error
    finally:
        if not execFlag:
            """
            Clean-up for program exit
            """
            if camEnableFlag:
                cam.terminate()
            gcl.terminate()
            mcul.terminate()
            break
