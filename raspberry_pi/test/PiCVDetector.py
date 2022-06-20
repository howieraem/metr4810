import cv2
import logging
import sys
import numpy as np

# to import from other directories
import os
sys.path.append(os.path.abspath('..//')) 
from conf.settings import CAM_Settings, PI_CV_Settings

if PI_CV_Settings.verbose:
    print("Logging to Console per Variable verbose=True")
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

class PiCVDetector(object):
    def __init__(self,
                 camshift_search_iter=10,
                 camshift_search_move=1):
        self.kf = cv2.KalmanFilter(4,2)
        self.kf.measurementMatrix = np.array([[1,0,0,0],
                                              [0,1,0,0]],np.float32)
        self.kf.transitionMatrix = np.array([[1,0,1,0],
                                             [0,1,0,1],
                                             [0,0,1,0],
                                             [0,0,0,1]],np.float32)
        self.kf.processNoiseCov = np.array([[1,0,0,0],
                                            [0,1,0,0],
                                            [0,0,1,0],
                                            [0,0,0,1]],np.float32) * 0.03
        self.measurement = np.array((2,1),np.float32)
        self.prediction = np.zeros((2,1),np.float32)
        self.kf_enabled = False
        self.term_crit = (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,
                          camshift_search_iter,
                          camshift_search_move)

    def findRectCentre(self, vertices):
        x = (vertices[0][0] + vertices[1][0] + vertices[2][0] + vertices[3][0]) / 4.0
        y = (vertices[0][1] + vertices[1][1] + vertices[2][1] + vertices[3][1]) / 4.0
        return np.array([np.float32(x), np.float32(y)], np.float32)
    
    def findPlacard(self,
                    vid_frame,
                    canny_thres1=50,
                    canny_thres2=200,
                    rect_ratio1=0.25,
                    rect_ratio2=0.4):
        self.width, self.height, _ = vid_frame.shape
        rect = []
        final = frame.copy()
        # Using HSV to grab white colour
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,np.array((0.,float(0),float(128))),
        np.array((180.,float(128),float(255))))

        # Obtain results and draw
        edged = cv2.Canny(mask,canny_thres1,canny_thres2)
        closed2 = cv2.morphologyEx(edged,cv2.MORPH_CLOSE,KERNEL_Dd7)  # Ensure edges are continuous
        _,contours,hierarchy = cv2.findContours(closed2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        for ctr in contours:
            perimeter = cv2.arcLength(ctr,True)
            # Assuming the ratio of placard size to image size is known
            if perimeter > rect_ratio1*(frame.shape[0]+frame.shape[1]) \
            and perimeter < rect_ratio2*(frame.shape[0]+frame.shape[1]):
                approx_shape = cv2.approxPolyDP(ctr,0.1*perimeter,True)
                if len(approx_shape) == 4:  # Quadrilateral,could add more conditions for rectangle
                    rect = approx_shape
                    cv2.drawContours(final,[rect],-1,(0,255,0),2)  # Draw the contour in green
                    #print(rect)
        return rect,final,mask
    
    #------------------------------------------------------------------------------
    def checkImageMatch(self, full_image, small_image):
        """
        Look for small_image in full_image and return best and worst results
        Try other PI_CV_Settings.MATCH_METHOD settings per config.py comments
        For More Info See
        http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
        """
        # Search for small image rectangle match in full size image
        result = cv2.matchTemplate(full_image, small_image, PI_CV_Settings.MATCH_METHOD)
        # Process result data and return probability values and
        # xy Location of best and worst image match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_loc, max_val

    #------------------------------------------------------------------------------
    def xyAtEdge(self, xy_loc):
        """ check if search rect is near edge plus buffer space """
        near_edge = False
        if (xy_loc[0] < CAM_Settings.sw_buf_x
                or xy_loc[0] > CAM_Settings.WIDTH - (CAM_Settings.sw_buf_x + CAM_Settings.sw_w)
                or xy_loc[1] < CAM_Settings.sw_buf_y
                or xy_loc[1] > CAM_Settings.HEIGHT - (CAM_Settings.sw_buf_y + CAM_Settings.sw_h)):
            near_edge = True
            logging.info("xy(%i,%i) xyBuf(%i,%i)",
                         xy_loc[0], xy_loc[1], CAM_Settings.sw_buf_x, CAM_Settings.sw_buf_y)
        return near_edge

    #------------------------------------------------------------------------------
    def xyLowVal(self, cur_val, val_setting):
        """ Check if maxVal is below PI_CV_Settings.MAX_SEARCH_THRESHOLD value """
        bad_match = False
        if cur_val < val_setting:
            bad_match = True
            logging.info("maxVal=%0.5f  threshold=%0.4f", cur_val, val_setting)
        return bad_match

    #------------------------------------------------------------------------------
    def xyMoved(self, xy_prev, xy_loc):
        """ Check if x or y location has changed """
        moved = False
        if (xy_loc[0] <> xy_prev[0] or
                xy_loc[1] <> xy_prev[1]):
            moved = True
            logging.info("dx=%i dy=%i ",
                         xy_loc[0] - xy_prev[0], xy_loc[1] - xy_prev[1])
        return moved

    #------------------------------------------------------------------------------
    def xyBigMove(self, xy_prev, xy_new):
        """ Check for large movements and set big_move """
        big_move = False
        if (abs(xy_new[0] - xy_prev[0]) > PI_CV_Settings.cam_move_x or
                abs(xy_new[1] - xy_prev[1]) > PI_CV_Settings.cam_move_y):
            big_move = True
            logging.info("xy(%i,%i) move exceeded %i or %i",
                         xy_new[0], xy_new[1], PI_CV_Settings.cam_move_x, PI_CV_Settings.cam_move_y)
        return big_move

    #------------------------------------------------------------------------------
    def xyUpdate(self, xy_cam, xy_prev, xy_new):
        """ Update xy position of camera based on original start position"""
        dx = 0
        dy = 0
        if abs(xy_prev[0] - xy_new[0]) > 0:
            dx = xy_prev[0] - xy_new[0]
        if abs(xy_prev[1] - xy_new[1]) > 0:
            dy = xy_prev[1] - xy_new[1]
        xy_cam = ((xy_cam[0] + dx, xy_cam[1] + dy))
        logging.info("cam xy (%i,%i) dxy(%i,%i)",
                     xy_cam[0], xy_cam[1], dx, dy)
        return xy_cam

    #------------------------------------------------------------------------------
    def camTrackOld(self, camera_link):
        """
        Process stream images in a while loop to find camera movement
        using an extracted search rectangle in the middle of one frame
        and find location in subsequent images.  Grab a new search rect
        as needed based on nearness to edge of image or percent probability
        of image search result Etc.
        """
        if PI_CV_Settings.WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
            big_w = int(CAM_Settings.WIDTH * PI_CV_Settings.WINDOW_BIGGER)
            big_h = int(CAM_Settings.HEIGHT * PI_CV_Settings.WINDOW_BIGGER)
        sw_max_val = PI_CV_Settings.MAX_SEARCH_THRESHOLD  # Threshold Accuracy of search in image
        xy_cam_pos = (0, 0)    # xy of Cam Overall Position
        xy_new = CAM_Settings.sw_xy    # xy of current search_rect
        xy_prev = xy_new  # xy of prev search_rect
        search_reset = False  # Reset search window back to center
        image1 = camera_link.getContCap()    # Grab image from video stream thread
        if image1 is None:
            return
        
        # Initialize centre search rectangle
        search_rect = image1[CAM_Settings.sw_y:CAM_Settings.sw_y+CAM_Settings.sw_h, CAM_Settings.sw_x:CAM_Settings.sw_x+CAM_Settings.sw_w]
        while True:
            image1 = camera_link.getContCap()  # Grab image from video stream thread or File
                
            xy_new, xy_val = self.checkImageMatch(image1, search_rect)
            # Analyse new xy for issues
            if self.xyMoved(xy_prev, xy_new):
                if (self.xyBigMove(xy_prev, xy_new) or
                        self.xyAtEdge(xy_new) or
                        self.xyLowVal(xy_val, sw_max_val)):
                    search_reset = True  # Reset search to center
                else:
                    # update new cam position
                    xy_cam_pos = self.xyUpdate(xy_cam_pos, xy_prev, xy_new)
                    xy_prev = xy_new
            if search_reset:   # Reset search_rect back to center
                if PI_CV_Settings.verbose and not PI_CV_Settings.log_only_moves:
                    logging.info("Reset search_rect img_xy(%i,%i) CamPos(%i,%i)",
                                 xy_new[0], xy_new[1],
                                 xy_cam_pos[0], xy_cam_pos[1])
                search_rect = image1[CAM_Settings.sw_y:CAM_Settings.sw_y+CAM_Settings.sw_h, CAM_Settings.sw_x:CAM_Settings.sw_x+CAM_Settings.sw_w]
                xy_new = CAM_Settings.sw_xy
                xy_prev = xy_new
                search_reset = False
            if PI_CV_Settings.verbose and not PI_CV_Settings.log_only_moves:
                logging.info("Cam Pos(%i,%i) %0.5f  img_xy(%i,%i)",
                             xy_cam_pos[0], xy_cam_pos[1],
                             xy_val, xy_new[0], xy_new[1])
            if PI_CV_Settings.window_on:
                image2 = image1
                # Display openCV window information on RPI desktop if required
                if PI_CV_Settings.show_circle:
                    cv2.circle(image2, (CAM_Settings.image_cx, CAM_Settings.image_cy), PI_CV_Settings.CIRCLE_SIZE, PI_CV_Settings.red, 1)
                if PI_CV_Settings.show_search_rect:
                    cv2.rectangle(image2, (xy_new[0], xy_new[1]),
                                  (xy_new[0] + CAM_Settings.sw_w, xy_new[1] + CAM_Settings.sw_h),
                                  PI_CV_Settings.green, PI_CV_Settings.LINE_THICKNESS)  # show search rect
                # Show Cam Position text on bottom of opencv window
                m_text = ("CAM POS(%i,%i)   " % (xy_cam_pos[0], xy_cam_pos[1]))
                cv2.putText(image2, m_text,
                            (CAM_Settings.image_cx - len(m_text) * 3, CAM_Settings.HEIGHT - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, PI_CV_Settings.CV_FONT_SIZE, PI_CV_Settings.green, 1)
                if PI_CV_Settings.WINDOW_BIGGER > 1:
                    image2 = cv2.resize(image2, (big_w, big_h))
                cv2.imshow('Cam-Track  (q in window to quit)', image2)
                if PI_CV_Settings.show_search_wind:
                    cv2.imshow('search rectangle', search_rect)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    def camTrack(self, frame, xy_cam_pos=None, xy_prev=None, search_rect=None):
        """
        Process individual input images to find camera movement
        using an extracted search rectangle in the middle of one frame
        and find location in subsequent images.  Grab a new search rect
        as needed based on nearness to edge of image or percent probability
        of image search result Etc. This function can be used explicitly.
        """
        if frame is None:
            return

        if xy_cam_pos is None or xy_prev is None:
            xy_cam_pos = (0, 0)
            xy_prev = CAM_Settings.sw_xy
            xy_new = xy_prev

        if search_rect is None:
            search_rect = frame[CAM_Settings.sw_y:CAM_Settings.sw_y+CAM_Settings.sw_h,
                                CAM_Settings.sw_x:CAM_Settings.sw_x+CAM_Settings.sw_w]

        if PI_CV_Settings.WINDOW_BIGGER > 1:  # Note setting a bigger window will slow the FPS
            big_w = int(CAM_Settings.WIDTH * PI_CV_Settings.WINDOW_BIGGER)
            big_h = int(CAM_Settings.HEIGHT * PI_CV_Settings.WINDOW_BIGGER)
        
        sw_max_val = PI_CV_Settings.MAX_SEARCH_THRESHOLD  # Threshold Accuracy of search in image

        #xy_new = CAM_Settings.sw_xy    # xy of current search_rect
        search_reset = False  # Reset search window back to center
        

        #while True:
        
        #image1 = camera_link.getContCap()  # Grab image from video stream thread or File
            
        xy_new, xy_val = self.checkImageMatch(frame, search_rect)
        # Analyse new xy for issues
        if self.xyMoved(xy_prev, xy_new):
            if (self.xyBigMove(xy_prev, xy_new) or
                    self.xyAtEdge(xy_new) or
                    self.xyLowVal(xy_val, sw_max_val)):
                search_reset = True  # Reset search to center
            else:
                # update new cam position
                xy_cam_pos = self.xyUpdate(xy_cam_pos, xy_prev, xy_new)
                #xy_prev = xy_new
        if search_reset:   # Reset search_rect back to center
            if PI_CV_Settings.verbose and not PI_CV_Settings.log_only_moves:
                logging.info("Reset search_rect img_xy(%i,%i) CamPos(%i,%i)",
                             xy_new[0], xy_new[1],
                             xy_cam_pos[0], xy_cam_pos[1])
            search_rect = frame[CAM_Settings.sw_y:CAM_Settings.sw_y+CAM_Settings.sw_h, CAM_Settings.sw_x:CAM_Settings.sw_x+CAM_Settings.sw_w]
            xy_new = CAM_Settings.sw_xy
            #xy_prev = xy_new
            #search_reset = False
        if PI_CV_Settings.verbose and not PI_CV_Settings.log_only_moves:
            logging.info("Cam Pos(%i,%i) %0.5f  img_xy(%i,%i)",
                         xy_cam_pos[0], xy_cam_pos[1],
                         xy_val, xy_new[0], xy_new[1])
        if PI_CV_Settings.window_on:
            image2 = frame
            # Display openCV window information on RPI desktop if required
            if PI_CV_Settings.show_circle:
                cv2.circle(image2, (CAM_Settings.image_cx, CAM_Settings.image_cy), PI_CV_Settings.CIRCLE_SIZE, PI_CV_Settings.red, 1)
            if PI_CV_Settings.show_search_rect:
                cv2.rectangle(image2, (xy_new[0], xy_new[1]),
                              (xy_new[0] + CAM_Settings.sw_w, xy_new[1] + CAM_Settings.sw_h),
                              PI_CV_Settings.green, PI_CV_Settings.LINE_THICKNESS)  # show search rect
            # Show Cam Position text on bottom of opencv window
            m_text = ("CAM POS(%i,%i)   " % (xy_cam_pos[0], xy_cam_pos[1]))
            cv2.putText(image2, m_text,
                        (CAM_Settings.image_cx - len(m_text) * 3, CAM_Settings.HEIGHT - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, PI_CV_Settings.CV_FONT_SIZE, PI_CV_Settings.green, 1)
            if PI_CV_Settings.WINDOW_BIGGER > 1:
                image2 = cv2.resize(image2, (big_w, big_h))
            cv2.imshow('Cam-Track  (q in window to quit)', image2)
            if PI_CV_Settings.show_search_wind:
                cv2.imshow('search rectangle', search_rect)
            #if cv2.waitKey(1) & 0xFF == 27:
                #break

        return xy_cam_pos, xy_new, search_rect
