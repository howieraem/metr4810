'''
    TCP video stream receiver script for ground station. Requires ffmpeg installed and added to PATH
'''
import numpy as np
import cv2
import subprocess as sp
import time

TCP_STREAM_ADDR = 'tcp://127.0.0.1:7000?listen=1?recv_buffer_size=4096'
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

tot_fail = 60

class FFMpegVideoCapture(object):
    def __init__(self, source, width, height, mode='bgr24'):
        x = ['ffmpeg']
        x.extend(['-i', source,
                  '-r', '7'
                  '-f', 'image2pipe',
                  '-pix_fmt', mode,
                  '-vcodec', 'rawvideo',
                  '-'])
        print(x)
        self.ffmpeg = sp.Popen(x, stdout=sp.PIPE, bufsize=16384)
        self.width = width
        self.height = height
        self.mode = mode
        if self.mode == "gray":
            self.dim = width*height
        elif self.mode == "bgr24":
            self.dim = width*height*3
        self.output = self.ffmpeg.stdout

    def read(self):
        if self.ffmpeg.poll():
            return False, None
        x = self.output.read(self.dim)
        if x == "":
            return False, None
        if self.mode == "gray":
            return True, np.frombuffer(x, dtype=np.uint8).reshape((self.height, self.width))
        elif self.mode == "bgr24":
            return True, (np.frombuffer(x, dtype=np.uint8).reshape((self.height, self.width, 3)))
        self.output.flush()


if __name__ == '__main__':
    vid = FFMpegVideoCapture(TCP_STREAM_ADDR, VIDEO_WIDTH, VIDEO_HEIGHT)
    scale = 0.5  # Avoid full screen
    num_fail = 0
    while True:
        ret, img = vid.read()
        if ret:
            num_fail = 0
            img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
            cv2.imshow('Frame', img)
            if cv2.waitKey(1) == 27:
                break
        else:
            num_fail += 1
            if num_fail >= tot_fail:
                print 'decoding failed'
                break
            print 'bad video'
            time.sleep(0.1)
    cv2.destroyAllWindows()
