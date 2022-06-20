"""
imageFeed.py

Widgets and processes for displaying the telescope datafeed.
"""

import sys
import os
sys.path.append(os.path.abspath('../'))
import numpy as np
import cv2
import subprocess as sp
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from conf.settings import GC_Settings


class FFMpegVideoCapture(object):
    """Start an ffmpeg subprocess to capture video stream
    """
    def __init__(self, source, width, height, mode='bgr24'):
        x = ['ffmpeg']
        x.extend(['-i', source,
                  '-f', 'image2pipe',
                  '-pix_fmt', mode,
                  '-vcodec', 'rawvideo',
                  '-'])
        self.ffmpeg = sp.Popen(x, stdout=sp.PIPE, bufsize=32768) #16384)
        self.width = width
        self.height = height
        self.mode = mode
        if self.mode == "gray":
            self.dim = width*height
        elif self.mode == "bgr24":
            self.dim = width*height*3
        self.output = self.ffmpeg.stdout
        # self.output, self.error = self.ffmpeg.communicate()

    def read(self):
        """Read frames from the video stream
        """
        if self.ffmpeg.poll():
            return False, None
        # Blocks on read
        x = self.output.read(self.dim)
        if x == "":
            return False, None
        if self.mode == "gray":
            return True, np.frombuffer(x, dtype=np.uint8)\
                    .reshape((self.height, self.width))
        elif self.mode == "bgr24":
            return True, (np.frombuffer(x, dtype=np.uint8)\
                    .reshape((self.height, self.width, 3)))
        self.output.flush()
        # _, self.error = self.ffmpeg.communicate()


class VideoThread(QThread):
    result = pyqtSignal(np.ndarray)
    failed = pyqtSignal()

    def __init__(self):
        super(VideoThread, self).__init__()
        self.vid = None

    def run(self):
        # print"Starting capture"
        self.vid = FFMpegVideoCapture(GC_Settings.TCP_STREAM_ADDR, 
                GC_Settings.VIDEO_WIDTH, GC_Settings.VIDEO_HEIGHT)
        # self.vid = cv2.VideoCapture("C:/Users/thebe/Google Drive/" + \
                # "ELEC4630/elec4630-assignment-1/Eric_Video.avi") # TODO
        tot_fail = 60
        num_fail = 0
        # Keep capturing until many consecutive frames fail or we quit
        while not GC_Settings.quit:
            ret, img = self.vid.read()
            if ret:
                num_fail = 0
                # Send signal to widget
                self.result.emit(img)
                # time.sleep(0.033)
            else:
                num_fail += 1
                if num_fail >= tot_fail:
                    print 'decoding failed'
                    # Send signal to widget
                    self.failed.emit()
                    break
                # print'bad video'
                # time.sleep(0.1)
        if self.vid.ffmpeg.poll() is None:
            self.vid.ffmpeg.kill() # TODO


class VideoFeedCV(object):
    def __init__(self):
        self.name = "Telescope Data Feed"
        self.window = None
        self.showing = False
        self.button = QPushButton("Show video feed")
        self.button.clicked.connect(self.toggleDisplay)
        self.btnReset = QPushButton("Reset video feed")
        self.btnReset.clicked.connect(self.restartVideo)
        self.video = VideoThread()
        self.video.start() # TODO
        self.video.result.connect(self.setFrame)
        self.video.failed.connect(self.restartVideo)
        self.quitting = False
        self.getting = False
        self.latestFrame = None
        self.frameReady = False
        self.roll = 0 # TODO 0 # rotate video by telescope roll

    def restartVideo(self):
        if not self.quitting:
            self.video.vid.ffmpeg.kill()
            self.quitting = True
        else:
            self.quitting = False
            print self.video.isRunning()
            self.video = VideoThread()
            self.video.start()
            self.video.result.connect(self.setFrame)
            self.video.failed.connect(self.restartVideo)

    def setFrame(self, frame):
        """Display a frame from the video stream
        """
        if self.showing:
            # Rotate image to compensate for telescope roll
            # self.roll += 0.1
            angle = -self.roll

            height, width = frame.shape[:2]
            image_center = (width/2, height/2)

            rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

            abs_cos = abs(rotation_mat[0,0])
            abs_sin = abs(rotation_mat[0,1])

            bound_w = int(height * abs_sin + width * abs_cos)
            bound_h = int(height * abs_cos + width * abs_sin)

            rotation_mat[0, 2] += bound_w/2 - image_center[0]
            rotation_mat[1, 2] += bound_h/2 - image_center[1]

            rotFrame = cv2.warpAffine(frame, rotation_mat, (bound_w, bound_h))
            cv2.imshow(self.name, rotFrame)

            if self.getting:
                print "Storing frame..."
                self.latestFrame = frame
                self.getting = False
                self.frameReady = True

    def prepareFrame(self):
        print "Preparing frame..."
        if self.showing:
            self.getting = True

    def getFrame(self, filename):
        print "Saving frame..."
        self.frameReady = False
        try:
            cv2.imwrite("images/" + filename, self.latestFrame)
        except:
            print "Failed to save frame"

    def open(self):
        """Enable video display
        """
        self.window = cv2.namedWindow(self.name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.name, 800, 600)
        self.showing = True
        self.button.setText("Close video feed")

    def close(self):
        """Disable video display
        """
        cv2.destroyWindow(self.name)
        self.showing = False
        self.button.setText("Show video feed")

    def toggleDisplay(self):
        if self.showing:
            self.close()
        else:
            self.open()


class ImageFeedWindow(QMainWindow):

    def __init__(self, mainWindow):
        super(ImageFeedWindow, self).__init__(mainWindow)
        self.setWindowTitle("Image Feed")
        self.setWindowIcon(QIcon("ui/astro.png"))
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.mainLayout = QGridLayout(self.centralwidget)
        self.imageLabel = QLabel("No image")
        self.imageLabel.setPixmap(QPixmap("C:/Users/thebe/" + \
                "projects/metr4810/ground_control/images/earth.jpg"))
        self.mainLayout.addWidget(self.imageLabel, 0, 0)
        self.showing = False
        self.button = QPushButton("Show video feed")
        self.button.clicked.connect(self.toggleDisplay)

        self.video = VideoThread()
        self.video.start()
        self.video.result.connect(self.setFrame)

    def setFrame(self, frame):
        # print"Setting frame"
        self.imageLabel.setPixmap(QPixmap.fromImage(frame))

    def toggleDisplay(self):
        if self.showing:
            self.close()
            self.showing = False
            self.button.setText("Show video feed")
        else:
            self.show()
            self.showing = True
            self.move(20, 20)
            self.button.setText("Close video feed")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            toggleDisplay()

    def closeEvent(self, e):
        self.showing = False
        e.accept()
        self.button.setText("Show video feed")

