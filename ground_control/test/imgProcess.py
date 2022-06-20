import cv2
import numpy as np
from skimage import restoration, img_as_ubyte, img_as_float

# Convolution matrices
KERNELd3 = np.ones((3,3),np.uint8)
KERNELd5 = np.ones((5,5),np.uint8)
KERNELd7 = np.ones((7,7),np.uint8)
KERNELd9 = np.ones((9,9),np.uint8)
KERNELd11 = np.ones((11,11),np.uint8)
KERNELd13 = np.ones((13,13),np.uint8)
KERNELd15 = np.ones((15,15),np.uint8)
KERNELd17 = np.ones((17,17),np.uint8)
KERNELd19 = np.ones((19,19),np.uint8)
KERNELd21 = np.ones((21,21),np.uint8)
KERNELd23 = np.ones((23,23),np.uint8)
KERNELd25 = np.ones((25,25),np.uint8)
KERNELd27 = np.ones((27,27),np.uint8)
SHARPEN_KERNEL1 = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
SHARPEN_KERNEL2 = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])

psf = np.ones((3, 3)) / 9

def adjustLevelLinear(img, contrast, brightness):
    img = np.int16(img)
    img = img*(contrast/127 + 1) - contrast + brightness
    img = np.clip(img, 0, 255)  # force all values to be between 0 and 255
    img = np.uint8(img)
    return img

def sharpen(src, gaussianSize, sigmaX, alpha, beta, gamma):
    mask = cv2.GaussianBlur(src, (gaussianSize,gaussianSize), sigmaX);
    dst = cv2.addWeighted(src, alpha, mask, beta, gamma)
    return dst


src = cv2.imread('13.jpeg', cv2.IMREAD_GRAYSCALE)
dst0 = adjustLevelLinear(src, 50, 15)
#dst1 = cv2.morphologyEx(dst0, cv2.MORPH_DILATE, KERNELd3)
dst2 = cv2.bilateralFilter(dst0, 5, 50, 50)
#dst3 = cv2.filter2D(dst2, -1, SHARPEN_KERNEL1)
dst3 = sharpen(dst2, 21, 3, 1.5, -0.5, 0)
dst4 = img_as_ubyte(restoration.richardson_lucy(img_as_float(dst2), psf))
cv2.imshow('source', src)
#cv2.imshow('destination0', dst0)
cv2.imshow('destination1', dst3)
cv2.imshow('destination2', dst4)
#cv2.imshow('destination2', dst4)


while True:
    if cv2.waitKey(1)==27:
        break
cv2.destroyAllWindows()
