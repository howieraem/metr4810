'''
    Script for simple VLC network streaming over UDP
'''
from GCLink import GCLink
import socket
import time
import numpy as np
import picamera
import cv2

#UDP_IP = "192.168.43.199"
#UDP_PORT = 8000

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.connect((UDP_IP, UDP_PORT))
#connection = sock.makefile('wb')
ground_station_connection = GCLink()
camera = picamera.PiCamera()
print('Camera and socket initialised.')

try:
        camera.resolution = (1920, 1080)
        camera.framerate = 8  # slightly below max rate at full frame
        camera.zoom = (0.25, 0.25, 0.5, 0.5)  # monocular issue
        print('Camera resolution set.')
        camera.start_preview()


        # If the exposure mode is 'sports', iso value is overwritten.
        # Sufficient power must be supplied to the Pi and the camera
        # with high shutter speed.
        #camera.iso = 800
        camera.exposure_mode = 'auto'
        camera.exposure_compensation = 25
        #camera.shutter_speed = 100  # must be faster than 1/fps if non-zero
        print('Camera shutter set')

        # Post-processing for noise removal
        camera.sharpness = 100
        camera.video_stabilization = True # translational only
        camera.saturation = -20
        #camera.brightness = 50
        print('Camera post-processing set. Warming up...')
        time.sleep(2)  # 2s warm-up
                
        # Start stream recording with mjpeg format due to H.264 level limit
        camera.start_recording(ground_station_connection,
                               format='h264',
                               bitrate=1200000)
        #camera.wait_recording(180)  # run for 30s
        while True:
                img = np.empty((240 * 320 * 3), dtype=np.uint8)
                camera.wait_recording(0.1)
                camera.capture(img, 'bgr', use_video_port=True,
                               resize=(320, 240))
                # Python 2.x doesn't allow multi-dimensional buffer objects
                img = img.reshape((240, 320, 3))
                cv2.imshow('Single', img)
                if cv2.waitKey(150) == 27:
                        break
        #camera.stop_recording()
finally:
        camera.close()
        cv2.destroyAllWindows()
        print('Camera recording stopped.')
        #connection.close()
        #sock.close()
        #print('Network communication closed.')
