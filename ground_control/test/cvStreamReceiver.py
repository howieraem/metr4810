'''
        Script for video stream UDP receiver. Requires OpenCV built with ffmpeg support
'''
import cv2

scale = 0.3

try:
    cap = cv2.VideoCapture('udp://@192.168.43.26:8000', cv2.CAP_FFMPEG)
    while True:
        ret, frame = cap.read()
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 10)
        if ret:
            frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(10) == 27:
                break
        else:
            break
finally:
    cv2.destroyAllWindows()
