'''
    Script for video target tracking and motion control. Green bounding box is actual location,
    blue bounding box is Camshift prediction,red bounding box is Kalman filter prediction, and
    Hough circle is yellow.
'''
from __future__ import division
import cv2
import numpy as np
import math

# Convolution matrices
kerneld3 = np.ones((3,3),np.uint8)
kerneld5 = np.ones((5,5),np.uint8)
kerneld7 = np.ones((7,7),np.uint8)
kerneld9 = np.ones((9,9),np.uint8)
kerneld11 = np.ones((11,11),np.uint8)
kerneld13 = np.ones((13,13),np.uint8)
kerneld15 = np.ones((15,15),np.uint8)
kerneld17 = np.ones((17,17),np.uint8)
kerneld19 = np.ones((19,19),np.uint8)
kerneld21 = np.ones((21,21),np.uint8)
kerneld23 = np.ones((23,23),np.uint8)
kerneld25 = np.ones((25,25),np.uint8)
kerneld27 = np.ones((27,27),np.uint8)

# Disable numpy uchar and uint8 wrapping around for overflow
def saturationCastUChar(number):
    if number > 255:
        number = 255
    elif number <0:
        number = 0
    return number

# Prevent pixel access to outside the image
def dimensionCast(idx, max_dimension):
    if idx >= max_dimension:
        idx = max_dimension - 1
    elif idx < 0:
        idx = 0
    return int(idx)

# Pixel-level linear brightness/contrast adjustment,not recommended for speed
def adjustLevelLin(img,alpha,beta):
    for y in range(0,img.shape[0]):
        for x in range(0,img.shape[1]):
            pix = img.item((y,x))
            new_pix = saturationCastUChar(alpha*pix + beta)
            img.itemset((y,x),new_pix)

# Pixel-level exponential brightness/contrast adjustment,not recommended for speed
def adjustLevelExp(img,alpha,beta):
    for y in range(0,img.shape[0]):
        for x in range(0,img.shape[1]):
            pix = img.item((y,x))
            new_pix = new_pix = saturationCastUChar(alpha*pow(pix,beta))
            img.itemset((y,x),new_pix)

# Return the center of a rectangle
def center(points):
    x = (points[0][0] + points[1][0] + points[2][0] + points[3][0]) / 4.0
    y = (points[0][1] + points[1][1] + points[2][1] + points[3][1]) / 4.0
    return np.array([np.float32(x), np.float32(y)], np.float32)

# Frame-wise processing
def processFrame(frame):
    rect = []
    final = frame.copy()
    # Using HSV to grab white colour
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,np.array((0.,float(0),float(128))),
    np.array((180.,float(128),float(255))))

    # Below is a much slower attempt of retrieving white colour
    #closed1 = cv2.morphologyEx(frame,cv2.MORPH_CLOSE,kerneld11)
    #blurred1 = cv2.medianBlur(closed1,5)
    #grey = cv2.cvtColor(blurred1,cv2.COLOR_BGR2GRAY)
    #adjustLevelLin(grey,5.12,-512)
    #_,binarized = cv2.threshold(grey,0,255,cv2.THRESH_OTSU)

    # Obtain results and draw
    edged = cv2.Canny(mask,50,200)
    closed2 = cv2.morphologyEx(edged,cv2.MORPH_CLOSE,kerneld7)  # Ensure edges are continuous
    _,contours,hierarchy = cv2.findContours(closed2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    for ctr in contours:
        perimeter = cv2.arcLength(ctr,True)
        # Assuming the ratio of placard size to image size is known
        if perimeter > 0.25*(frame.shape[0]+frame.shape[1]) \
        and perimeter < 0.4*(frame.shape[0]+frame.shape[1]):
            approx_shape = cv2.approxPolyDP(ctr,0.1*perimeter,True)
            if len(approx_shape) == 4:  # Quadrilateral,could add more conditions for rectangle
                rect = approx_shape
                cv2.drawContours(final,[rect],-1,(0,255,0),2)  # Draw the contour in green
                #print(rect)
    return rect,final,mask

# Initialize a Kalman filter object
def setupKalmanFilter():
    kf = cv2.KalmanFilter(4,2)
    kf.measurementMatrix = np.array([[1,0,0,0],
                                    [0,1,0,0]],np.float32)
    kf.transitionMatrix = np.array([[1,0,1,0],
                                    [0,1,0,1],
                                    [0,0,1,0],
                                    [0,0,0,1]],np.float32)
    kf.processNoiseCov = np.array([[1,0,0,0],
                                    [0,1,0,0],
                                    [0,0,1,0],
                                    [0,0,0,1]],np.float32) * 0.03
    measurement = np.array((2,1),np.float32)
    prediction = np.zeros((2,1),np.float32)
    return kf,measurement,prediction

# Main loop for video processing, set a fps preference <= max fps due to computing power limit
def processVideo(stream_name, fps_pref=30, scale=0.5):
    box=[]
    kf_enabled=False
    vid = cv2.VideoCapture(stream_name)
    # Termination criteria for Camshift search, either 10 iteration or move by at least 1 pt
    term_crit = (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.5)
    
    # Check access to the stream
    if (vid.isOpened()== False): 
        print('Error opening video stream')
        return
    fps = vid.get(cv2.CAP_PROP_FPS)
    if fps_pref >= fps:
        multiplier = 1
    else:
        multiplier = fps/fps_pref # Integer preferred, set fps_pref accordingly
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    marginX = scale*width*0.5
    marginY = scale*height*0.5
        
    # Keep processing until interrupted or done
    while (vid.isOpened()):
        frame_id = int(round(vid.get(1)))
        ret,frame = vid.read()
        if ret == True:
            if frame_id % multiplier == 0:
                scaled = cv2.resize(frame,(0,0),fx=scale,fy=scale)
                rect, processed, mask = processFrame(scaled)
                # When a target's contour is first found, set the initial tracking window
                if len(rect) > 1 and kf_enabled == False:
                    # Take the diagonal points
                    box.append(rect[0][0].tolist())
                    box.append(rect[2][0].tolist())
                    # The indexing below depends on whether rectangle height > length or not
                    cropped = scaled[int(box[0][1]-marginX):int(box[1][1]+marginX),
                                    int(box[1][0]-marginY):int(box[0][0]+marginY)].copy()
                    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
                    cropped_mask = mask[int(box[0][1]-marginX):int(box[1][1]+marginX),
                                    int(box[1][0]-marginY):int(box[0][0]+marginY)].copy()
                    cropped_hist = cv2.calcHist([cropped],[0,1],cropped_mask,[180,255],[0,180,0,255])
                    cv2.normalize(cropped_hist,cropped_hist,0,255,cv2.NORM_MINMAX)
                    track_window = (int(box[1][0]-marginX),int(box[0][1]-marginY),
                                    int(box[0][0]-box[1][0]+marginX),int(box[1][1]-box[0][1]+marginY))
                    kf,measurement,prediction = setupKalmanFilter()
                    kf_enabled = True
                # Keep predicting
                elif kf_enabled == True:
                    hsv = cv2.cvtColor(scaled, cv2.COLOR_BGR2HSV)
                    bproject = cv2.calcBackProject([hsv],[0,1],cropped_hist,[0,180,0,255],1)
                    #cv2.imshow('Back projection',bproject)
                    ret, track_window = cv2.CamShift(bproject, track_window, term_crit)
                    x,y,w,h = track_window
                    cv2.rectangle(processed,(x,y),(x+w,y+h),(255,0,0),2)  # Blue for Camshift
                    pts = cv2.boxPoints(ret)
                    pts = np.int0(pts)
                    kf.correct(center(pts))
                    prediction = kf.predict()
                    # Red for Kalman filter
                    cv2.rectangle(processed,(prediction[0]-(0.5*w),prediction[1]-(0.5*h)),
                                  (prediction[0]+(0.5*w),prediction[1]+(0.5*h)),(0,0,255),2)

                # Try detecting circles
                grey = cv2.cvtColor(scaled,cv2.COLOR_BGR2GRAY)
                grey_blurred = cv2.medianBlur(grey, 9)
                # Assuming the ratio of circle size to image size is known
                min_radius = int(0.01*scale*width)
                max_radius = int(0.012*scale*width)
                circles = cv2.HoughCircles(grey_blurred,cv2.HOUGH_GRADIENT,1,100,100,400,
                                           min_radius,max_radius)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for ccl in circles[0,:]:
                        # The radius limits above may not work, double-check here.
                        # For some weird reasons, the conditions below work better.
                        if ccl[2] < max_radius*2 and ccl[2] > min_radius:
                            # Draw in yellow
                            cv2.circle(processed,(ccl[0],ccl[1]),ccl[2],(0,255,255),2)
                
                cv2.imshow('Frame',processed)
                key = cv2.waitKey(int(1000/fps_pref)) & 0xff
                if key == 27:  # Press 'Esc' to quit
                    break
        else: 
            break

    # Clean-up
    vid.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    processVideo('test_vid.mp4',scale=0.2)
