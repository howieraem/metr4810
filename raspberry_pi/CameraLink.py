"""
METR4810 
Module for Raspberry Pi camera (imaging system).
"""
# Import primitive modules
import picamera
from picamera.array import PiRGBArray
import numpy as np
import time
import sys
import os
import errno
import socket

# Import settings from another directory
sys.path.append(os.path.abspath('..//'))
from conf.settings import CAM_Settings

class CameraLink(object):
    """
    Class for camera object functionality.
    """
    def __init__(self,
                 cont_res=(CAM_Settings.WIDTH, CAM_Settings.HEIGHT)):
        """
        Constructor of the class. Set the default parameters to the
        camera and warm it up.
        :param cont_res: Resolution of continuous capture.
        """
        self.camera = picamera.PiCamera()
        print 'Camera connected'
        self.is_recording_vid = False
        self.cont_array = PiRGBArray(self.camera, size=cont_res)
        self.cont_stream = None
        self.is_cont_capturing = False
        self.setFrame()
        print 'Camera frame parameters set'
        self.setShutter()
        print 'Camera shutter parameters set'
        self.setProcessing()
        print 'Camera pre-processing parameters set'
        self.warmUp()
        print 'Camera warmed'
            
    def setFrame(self,
                 resolution=CAM_Settings.FULL_RES,
                 framerate=CAM_Settings.FULL_FRAMERATE,
                 rotation=CAM_Settings.ROTATION):
        """
        Set frame parameters with defaults from settings.
        :param resolution: Full sensor resolution
        :param framerate: Maximum framerate at the full resolution
        :param rotation: Angle to rotate the frame
        :return
        """
        try:
            self.camera.resolution = resolution
        except picamera.PiCameraError:
            self.camera.resolution = (2592, 1944)
        self.camera.framerate = framerate
        self.camera.rotation = rotation

    def getFrameInfo(self):
        """
        Retrieves current frame parameters.
        :return: Tuple containing the full resolution and the maximum framerate
        """
        return (self.camera.resolution,
                self.camera.framerate)

    def setShutter(self,
                   exposure_mode=CAM_Settings.EXPOSURE_MODE,
                   exposure_compensation=CAM_Settings.EXPOSURE_COMPENSATION,
                   iso=CAM_Settings.ISO,
                   shutter_speed=CAM_Settings.SHUTTER_SPEED,
                   white_balance_mode=CAM_Settings.WHITE_BAL_MODE,
                   dynamic_range=CAM_Settings.DYNAMIC_RANGE,
                   meter_mode=CAM_Settings.METER_MODE):
        """
        Set shutter parameters with defaults from settings.
        :param exposure_mode: Algorithm to calculate exposure time
        :param exposure_compensation: Exposure adjustment
        :param iso: Sensitivity
        :param shutter_speed: The inverse of exposure time
        :param white_balance_mode: Algorithm to calculate gain
        :param dynamic_range: Accommodation to various exposures
        :param meter_mode: Sampling algorithm for exposure time calculations
        :return
        """
        self.camera.exposure_mode = exposure_mode
        self.camera.exposure_compensation = exposure_compensation
        self.camera.iso = iso
        self.camera.shutter_speed = shutter_speed
        self.camera.awb_mode = white_balance_mode
        self.camera.drc_strength = dynamic_range
        self.camera.meter_mode = meter_mode
        
    def getShutterInfo(self):
        """
        Retrieves current shutter parameters.
        :return: Tuple containing exposure mode, exposure compensation, ISO,
        shutter speed, white balance mode, dynamic range and meter mode.
        """
        return (self.camera.exposure_mode,
                self.camera.exposure_compensation,
                self.camera.iso,
                self.camera.shutter_speed,
                self.camera.awb_mode,
                self.camera.drc_strength,
                self.camera.meter_mode)

    def setProcessing(self,
                      sharpness=CAM_Settings.SHARPNESS,
                      saturation=CAM_Settings.SATURATION,
                      brightness=CAM_Settings.BRIGHTNESS,
                      contrast=CAM_Settings.CONTRAST,
                      video_stabilization=CAM_Settings.STABILIZATION,
                      image_effect=CAM_Settings.IMAGE_EFFECT):
        """
        Set image pre-processing parameters with defaults from settings.
        :param sharpness
        :param saturation
        :param brightness
        :param contrast
        :param video_stabilization
        :param image_effect
        :return
        """
        self.camera.sharpness = sharpness
        self.camera.saturation = saturation
        self.camera.brightness = brightness
        self.camera.contrast = contrast
        self.camera.video_stabilization = video_stabilization
        self.camera.image_effect = image_effect

    def getProcessingInfo(self):
        """
        Retrieves current image pre-processing parameters.
        :return: Tuple containing sharpness, saturation, brightness,
        contrast, video stabilization and image effect.
        """
        return (self.camera.sharpness,
                self.camera.saturation,
                self.camera.brightness,
                self.camera.contrast,
                self.camera.video_stabilization,
                self.camera.image_effect)

    def recordVideoStream(self,
                          link,
                          encoding=CAM_Settings.VID_ENCODING,
                          bitrate=CAM_Settings.ENCODE_BITRATE,
                          quality=CAM_Settings.QUALITY,
                          resolution=(CAM_Settings.VIDEO_WIDTH,
                                      CAM_Settings.VIDEO_HEIGHT)):
        """
        Record video to the network.
        :param link: Connection link object
        :param encoding: Encoding format of video
        :param bitrate: Video encoding bit rate
        :param quality: Video quality
        :param resolution: Video resolution
        :param level: Encoding level, for H.264 only
        :return
        """
        connected = False
        while not connected:
            try:
                link.connectStreamSocket()
                connected = True
            except socket.timeout:
                print 'Video socket timed out, trying to reconnect'
                pass
        


        self.camera.start_recording(link.stream_conn,
                                    format=encoding,
                                    bitrate=bitrate,
                                    quality=quality,
                                    resize=resolution)
        self.is_recording_vid = True
        while connected:
            try:
                time.sleep(1)
            except socket.error as serr:
                if serr.errno == errno.ECONNRESET:
                    print 'Video connection dropped, reconnecting'
                    link.sock_stream.close()
                    link.connectStreamSocket()
                else:
                    connected = False
                    self.stopRecordingVideo()
                    raise  # Unexpected error

    def stopRecordingVideo(self):
        """
        Stop recording video.
        :return
        """
        self.camera.stop_recording()
        self.is_recording_vid = False

    def captureStillImageArray(self,
                               encoding=CAM_Settings.ARRAY_ENCODING,
                               resolution=CAM_Settings.FULL_RES,
                               multicast_delay=CAM_Settings.MULTICAST_DELAY):
        """
        Capture a still image in raw numpy array format.
        :param encoding: Colour channels setting
        :param resolution
        :param multicast_delay: Delay time when there is a video being streamed.
        :return
        """
        if self.is_recording_vid:  # Avoid freezing the camera
            self.camera.wait_recording(multicast_delay)
        rawArray = np.empty((resolution[1]*resolution[0]*3),
                            dtype=np.unit8)
        self.camera.wait_recording(multicast_delay)
        self.camera.capture(rawArray,
                            encoding,
                            use_video_port=self.is_recording_vid,
                            resize=resolution)
        img = rawArray.reshape((resolution[1], resolution[0], 3))
        return img

    def captureStillImageFile(self,
                              io_object,
                              encoding=CAM_Settings.IMG_FILE_ENCODING,
                              resolution=CAM_Settings.FULL_RES,
                              multicast_delay=CAM_Settings.MULTICAST_DELAY):
        """
        Capture a still image in the file form.
        :param io_object: FILE* like object, can be filename or network socket
        :param encoding: Image file format
        :param resolution
        :param multicast_delay: Delay time when there is a video being streamed.
        :return
        """
        if self.is_recording_vid:  # Avoid freezing the camera
            self.camera.wait_recording(multicast_delay)
        # Check if input is a file name or a socket
        if isinstance(io_object, basestring):
            # Ensure backend is the same as format
            io_object = io_object + '.' + encoding
        self.camera.capture(io_object,
                            format=encoding,
                            use_video_port=self.is_recording_vid,
                            resize=resolution)
        if self.is_recording_vid:  # Avoid freezing the camera
            self.camera.wait_recording(multicast_delay)
    
    def startContCap(self,
                     encoding=CAM_Settings.ARRAY_ENCODING,
                     resolution=(CAM_Settings.WIDTH, CAM_Settings.HEIGHT),
                     multicast_delay=CAM_Settings.MULTICAST_DELAY):
        """
        Set up continuous capture.
        :param encoding: Format of the image, can be numpy array or file
        :param resolution
        :param multicast_delay: Delay time when there is a video being streamed.
        :return
        """
        self.is_cont_capturing = True
        if self.is_recording_vid:  # Avoid freezing the camera
            self.camera.wait_recording(multicast_delay)
        self.cont_stream = self.camera.capture_continuous(self.cont_array,
                                                          format=encoding,
                                                          use_video_port=True,
                                                          resize=resolution)
    
    def getContCap(self,
                   multicast_delay=CAM_Settings.MULTICAST_DELAY):
        """
        Retrieve next frame of the continuous capture.
        :param multicast_delay: Delay time when there is a video being streamed.
        :return: The frame captured
        """
        if self.cont_stream is not None and self.is_cont_capturing:
            frame = self.cont_stream.next().array
            self.cont_array.truncate(0)
            if self.is_recording_vid:  # Avoid freezing the camera
                self.camera.wait_recording(multicast_delay)
            return frame
        else:
            print 'Please call CameraLink().startContCap() first'

    def stopContCap(self):
        """
        Disable continuous capture.
        :return
        """
        self.cont_stream.close()
        self.cont_array.close()
        self.is_cont_capturing = False
                                
    def warmUp(self,
               warm_up_time=CAM_Settings.WARM_UP_TIME):
        """
        Pause before recording or capturing since the camera needs to calculate
        attributes for various lighting conditions.
        :param warm_up_time: Delay time
        :return
        """
        time.sleep(warm_up_time)

    def terminate(self):
        """
        Free the memory once the main program terminates.
        :return
        """
        self.is_recording_vid = False
        if self.cont_stream is not None and self.cont_array is not None:
            self.stopContCap()
        self.camera.close()

    def isTerminated(self):
        """
        Check if the camera has been closed.
        :return: Boolean
        """
        return self.camera.closed()
