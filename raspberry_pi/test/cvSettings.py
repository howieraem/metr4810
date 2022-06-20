class PI_CV_Settings(object):
    # Convolution matrices
    KERNEL_D3 = np.ones((3,3),np.uint8)
    KERNEL_D5 = np.ones((5,5),np.uint8)
    KERNEL_D7 = np.ones((7,7),np.uint8)
    KERNEL_D9 = np.ones((9,9),np.uint8)
    KERNEL_D11 = np.ones((11,11),np.uint8)
    KERNEL_D13 = np.ones((13,13),np.uint8)
    KERNEL_D15 = np.ones((15,15),np.uint8)
    KERNEL_D17 = np.ones((17,17),np.uint8)
    KERNEL_D19 = np.ones((19,19),np.uint8)
    KERNEL_D21 = np.ones((21,21),np.uint8)
    KERNEL_D23 = np.ones((23,23),np.uint8)
    KERNEL_D25 = np.ones((25,25),np.uint8)
    KERNEL_D27 = np.ones((27,27),np.uint8)
    
    window_on = True      # True=Display OpenCV Windows (GUI desktop reqd) False=Terminal Only
    verbose = True         # True=Turn on logging messages False=Turn Off logging messages
    log_only_moves = True  # Log True=Only Cam Moves False=All
    
    # Sets the maximum x y pixels that are allowed to reduce effect of objects moving in frame
    cam_move_x = 30        # Max number of x pixels in one move
    cam_move_y = 30         # Max number of y pixels in one move

    # OpenCV Settings
    # ---------------
    show_search_rect = True  # show outline of current search box on main window
    show_search_wind = False # True=Show search_rect GUI window  False=Window not Shown
    show_circle = True       # Show a circle otherwise show bounding rectangle on window
    CIRCLE_SIZE = 3          # diameter of circle to show location in window
    WINDOW_BIGGER = 1.0      # Increase the display window size multiplier default=2.0
    LINE_THICKNESS = 1       # Thickness of bounding line in pixels default=1
    CV_FONT_SIZE = .25       # size of font on opencv window default=.25
    red = (0,0,255)          # opencv line colours
    green = (0,255,0)
    blue = (255,0,0)

    # OpenCV MatchTemplate Settings
    # -----------------------------
    MAX_SEARCH_THRESHOLD = .96 # default=.97 Accuracy for best search result of search_rect in stream images
    MATCH_METHOD = 3
                # Valid MatchTemplate COMPARE_METHOD Int Values
                # ---------------------------------------------
                # 0 = cv2.TM_SQDIFF  = 0
                # 1 = cv2.TM_SQDIFF_NORMED = 1
                # 2 = cv2.TM_CCORR = 2
                # 3 = cv2.TM_CCORR_NORMED = 3    Default
                # 4 = cv2.TM_CCOEFF = 4
                # 5 = cv2.TM_CCOEFF_NORMED = 5
                #
                # For other comparison methods 
                # see http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
