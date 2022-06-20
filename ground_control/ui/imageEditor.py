"""
imageEditor.py

Expanded interface for image viewing and processing
"""

import sys
import os
if __name__ == '__main__':
    sys.path.append(os.path.abspath('../../'))
else:
    sys.path.append(os.path.abspath('../')) # to import from other directories
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image, ImageQt, ImageEnhance
from conf.settings import GC_Settings

import cv2
import numpy as np


class ImageEditorSlider(QSlider):

    def __init__(self, valMin=1, valMax=100, val=100, interval=1):
        super(ImageEditorSlider, self).__init__(Qt.Horizontal)
        self.setMinimum(valMin)
        self.setMaximum(valMax)
        self.setValue(val)
        self.val = val
        # self.setTickPosition(QSlider.TicksBelow)
        self.setTickInterval(interval)

    def reset(self):
        self.setValue(self.val)


class ImageEditor(QWidget):
    """Widget for image viewing and processing
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)

        self.imageOG = None # original image
        self.imageCV = None # global reference for improc functions
        self.imageUA = None # adjustment reference
        self.imageSH = None # sharpening reference
        self.latestFunction = None

        self.sliderScale = ImageEditorSlider(1, 200, 100)
        self.sliderScale.valueChanged.connect(self.scale)
        self.lblScale = QLabel("Scale: 100%")
        self.previousScale = self.sliderScale.val
        self.sliderRotate = ImageEditorSlider(0, 359, 0)
        self.sliderRotate.valueChanged.connect(self.rotate)
        self.lblAngle = QLabel("Angle: 0 deg")
        self.previousAngle = self.sliderRotate.val

        self.sliderBrightness = ImageEditorSlider(0, 100, 50)
        self.sliderBrightness.valueChanged.connect(self.changeBrightness)
        self.lblBrightness = QLabel("Brightness: 50%")
        self.sliderContrast = ImageEditorSlider(0, 100, 0)
        self.sliderContrast.valueChanged.connect(self.changeContrast)
        self.lblContrast = QLabel("Contrast: 0%")

        self.sliderSharpen = ImageEditorSlider(1, 45, 1)
        self.sliderSharpen.valueChanged.connect(self.sharpen)
        self.lblSharpen = QLabel("Gaussian size: {}".format(
                self.sliderSharpen.val))

        self.sliderDAngle = ImageEditorSlider(0, 180, 0)
        self.sliderDAngle.valueChanged.connect(self.changeDAngle)
        self.lblDAngle = QLabel("D.Angle: 0 deg")
        self.sliderDD = ImageEditorSlider(1, 10, 1)
        self.sliderDD.valueChanged.connect(self.changeDD)
        self.lblDD = QLabel("D.d: 1")
        self.sliderDSNR = ImageEditorSlider(0, 20, 0)
        self.sliderDSNR.valueChanged.connect(self.changeDSNR)
        self.lblDSNR = QLabel("D.SNR: 0 dB")

        self.btnReset = QPushButton("Reset")
        self.btnReset.clicked.connect(self.showImageT(True))

        self.sliders = [self.sliderScale, self.sliderRotate,
                self.sliderBrightness, self.sliderContrast,
                self.sliderSharpen, self.sliderDAngle, 
                self.sliderDD, self.sliderDSNR]
        self.labels = [self.lblScale, self.lblAngle, self.lblBrightness,
                self.lblContrast, self.lblDAngle, self.lblDD, self.lblDSNR]
        for lbl in self.labels:
            lbl.setFixedWidth(100)

        sliderWrapper = QWidget()
        sliderLayout = QGridLayout(sliderWrapper)

        sliderLayout.addWidget(self.sliderScale, 0, 0)
        sliderLayout.addWidget(self.lblScale, 0, 1)
        sliderLayout.addWidget(self.sliderRotate, 1, 0)
        sliderLayout.addWidget(self.lblAngle, 1, 1)
        sliderLayout.addWidget(self.sliderBrightness, 2, 0)
        sliderLayout.addWidget(self.lblBrightness, 2, 1)
        sliderLayout.addWidget(self.sliderContrast, 3, 0)
        sliderLayout.addWidget(self.lblContrast, 3, 1)

        sliderLayout.addWidget(self.sliderSharpen, 0, 2)
        sliderLayout.addWidget(self.lblSharpen, 0, 3)
        sliderLayout.addWidget(self.sliderDAngle, 1, 2)
        sliderLayout.addWidget(self.lblDAngle, 1, 3)
        sliderLayout.addWidget(self.sliderDD, 2, 2)
        sliderLayout.addWidget(self.lblDD, 2, 3)
        sliderLayout.addWidget(self.sliderDSNR, 3, 2)
        sliderLayout.addWidget(self.lblDSNR, 3, 3)

        sliderLayout.addWidget(self.btnReset, 4, 0, 1, 2)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(sliderWrapper)

        self.setLayout(layout)

    def showImageT(self, reset):
        """Wrapper to parse argument from Qt signal
        """
        return lambda : self.showImage(reset=reset)

    def showImage(self, filename=None, reset=False):
        """Show an image from file or reset image to original view
        """
        self.scene.clear()
        if reset:
            if self.imageOG is None:
                return
            self.imageCV = self.imageOG.copy()
            for s in self.sliders:
                s.reset()
        else:
            print "Showing full image in separate window"
            # TODO
            path = os.path.abspath("images/" + filename).replace("\\", "/")
            self.imageOG = cv2.imread(path, 0)
            if self.imageOG is None:
                print "Could not load image", path
                return
            self.imageCV = self.imageOG.copy()

        self.imageUA = self.imageCV.copy()
        self.imageSH = self.imageCV.copy()

        image = self.imageCV
        if self.isColor(image):
            # print image.shape
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imFormat = QImage.Format_RGB888
            # print "Colour", imFormat
            numBytes = 3
        else:
            # print image.shape
            imFormat = QImage.Format_Grayscale8
            # print "Grayscale", imFormat
            numBytes = 1

        qimage = QImage(image.data, image.shape[1], image.shape[0],
                image.shape[1] * numBytes, imFormat)
        pixMap = QPixmap(qimage)

        self.item = self.scene.addPixmap(pixMap)
        self.view.fitInView(QRectF(0, 0, image.shape[1], image.shape[0]),
                Qt.KeepAspectRatio)
        self.view.setTransform(QTransform.fromScale(1.0, 1.0))
        self.scene.update()

    def scale(self):
        self.latestFunction = self.scale
        s = self.sliderScale.value() / float(self.previousScale)
        self.previousScale = self.sliderScale.value()
        self.lblScale.setText("Scale: {0:.1f}%".format(self.previousScale))
        currentTransform = self.view.transform()
        currentTransform.scale(s, s)
        self.view.setTransform(currentTransform)
        self.scene.update()

    def rotate(self):
        self.latestFunction = self.rotate
        t = self.sliderRotate.value() - self.previousAngle
        self.previousAngle = self.sliderRotate.value()
        self.lblAngle.setText("Angle: {0:.1f} deg".format(self.previousAngle))
        # print t
        currentTransform = self.view.transform()
        currentTransform.rotate(t)
        self.view.setTransform(currentTransform)
        self.scene.update()

    def changeBrightness(self):
        cs = self.sliderContrast.value()
        bs = self.sliderBrightness.value()
        self.lblBrightness.setText("Brightness: {}%".format(bs))
        if bs == self.sliderBrightness.val:
            return
        self.adjust(cs, bs)

    def changeContrast(self):
        cs = self.sliderContrast.value()
        bs = self.sliderBrightness.value()
        self.lblContrast.setText("Contrast: {}%".format(cs))
        if cs == self.sliderContrast.val:
            return
        self.adjust(cs, bs)

    def adjust(self, contrast, brightness):
        """Adjust image brightness and contrast
        """
        if self.imageCV is None or self.imageUA is None:
            return
        contrast = 255 * contrast / 100.0
        brightness = 255 * (brightness - 50) / 100
        if self.latestFunction == self.adjust:
            img = self.imageUA.copy()
        else:
            img = self.imageCV.copy()
        img = np.int16(img)
        img = img * (contrast / 127 + 1) - contrast + brightness
        img = np.clip(img, 0, 255)  # force all values to [0, 255]
        img = np.uint8(img)
        self.imageCV = img
        self.imageSH = self.imageCV.copy()
        self.latestFunction = self.adjust
        self.update(img)

    def sharpen(self):
        """Compound the image with blur to produce a sharpening effect
        """
        g = self.sliderSharpen.value()
        if g % 2 == 0:
            g -= 1
        self.lblSharpen.setText("Gaussian size: {}".format(g))
        if g == self.sliderSharpen.val:
            return
        if self.imageCV is None:
            return
        if self.latestFunction == self.sharpen:
            img = self.imageSH.copy()
        else:
            img = self.imageCV.copy()
        sigmaX = 3
        alpha = 1.5
        beta = -0.5
        gamma = 0
        mask = cv2.GaussianBlur(img, (g, g), sigmaX);
        img = cv2.addWeighted(img, alpha, mask, beta, gamma)
        self.imageCV = img
        self.imageUA = self.imageCV.copy()
        self.latestFunction = self.sharpen
        self.update(img)

    def changeDAngle(self):
        """Change the angle for deconvolution
        """      
        ang = self.sliderDAngle.value()
        d = self.sliderDD.value()
        noise = self.sliderDSNR.value()
        self.lblDAngle.setText("D.Angle: {} deg".format(ang))
        if ang == self.sliderDAngle.val:
            return
        self.deconvolve(ang, d, noise)

    def changeDD(self):
        """Change the magnitude (kernel size) for deconvolution
        """
        ang = self.sliderDAngle.value()
        d = self.sliderDD.value()
        noise = self.sliderDSNR.value()
        self.lblDD.setText("D.d: {}".format(d))
        # print d
        if d == self.sliderDD.val:
            return
        self.deconvolve(ang, d, noise)

    def changeDSNR(self):
        """Change the signal-to-noise ratio for deconvolution
        """
        ang = self.sliderDAngle.value()
        d = self.sliderDD.value()
        noise = self.sliderDSNR.value()
        self.lblDSNR.setText("D.SNR: {} dB".format(noise))
        if noise == self.sliderDSNR.val:
            return
        self.deconvolve(ang, d, noise)

    def blurEdge(self, img, d=31):
        """Perform a weighted blur on image

        Based on:
        https://github.com/michal2229/dft-wiener-deconvolution-with-psf
        """
        h, w  = img.shape[:2]
        img_pad = cv2.copyMakeBorder(img, d, d, d, d, cv2.BORDER_WRAP)
        img_blur = cv2.GaussianBlur(img_pad, (2*d+1, 2*d+1), -1)[d:-d,d:-d]
        y, x = np.indices((h, w))
        dist = np.dstack([x, w-x-1, y, h-y-1]).min(-1)
        w = np.minimum(np.float32(dist)/d, 1.0)
        return img*w + img_blur*(1-w)

    def motionKernel(self, angle, d, sz=65):
        """Make a kernel for motion

        Based on:
        https://github.com/michal2229/dft-wiener-deconvolution-with-psf
        """
        kern = np.ones((1, d), np.float32)
        c, s = np.cos(angle), np.sin(angle)
        A = np.float32([[c, -s, 0], [s, c, 0]])
        sz2 = sz // 2
        A[:,2] = (sz2, sz2) - np.dot(A[:,:2], ((d-1)*0.5, 0))
        kern = cv2.warpAffine(kern, A, (sz, sz), flags=cv2.INTER_CUBIC)
        return kern

    def defocusKernel(self, d, sz=65):
        """Make a kernel for defocusing

        Based on:
        https://github.com/michal2229/dft-wiener-deconvolution-with-psf
        """
        kern = np.zeros((sz, sz), np.uint8)
        cv2.circle(kern, (sz, sz), d, 255, -1, cv2.LINE_AA, shift=1)
        kern = np.float32(kern) / 255.0
        return kern

    def deconvolve(self, ang, d, noise):
        """Deconvolve an image to reduce motion blur

        Based on:
        https://github.com/michal2229/dft-wiener-deconvolution-with-psf
        """

        if self.imageCV is None:
            return
        # print "Deconvolving"

        ang = np.deg2rad(ang)
        d = d
        noise = 10 ** (-0.1 * noise)
        # print ang, d, noise

        defocus = False # Radial or not

        img = self.imageCV.copy()
        if self.isColor(img):
            img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_bw = img
        img_bw = np.float32(img_bw) / 255.0
        img_bw = self.blurEdge(img_bw)

        # if self.latestFunction != self.deconvolve:
        #     # Only take DFT the first time while adjusting sliders
        #     # print "Taking dft"
        self.IMG_BW = cv2.dft(img_bw, flags=cv2.DFT_COMPLEX_OUTPUT)

        if defocus:
            psf = self.defocusKernel(d)
        else:
            psf = self.motionKernel(ang, d)

        psf /= psf.sum()
        psf_pad = np.zeros_like(img_bw)
        kh, kw = psf.shape
        psf_pad[:kh, :kw] = psf
        PSF = cv2.dft(psf_pad, flags=cv2.DFT_COMPLEX_OUTPUT, nonzeroRows=kh)
        PSF2 = (PSF**2).sum(-1)
        iPSF = PSF / (PSF2 + noise)[...,np.newaxis]

        RES_BW = cv2.mulSpectrums(self.IMG_BW, iPSF, 0)
        res_bw = cv2.idft(RES_BW, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        res_bw = np.roll(res_bw, -kh//2, 0)
        res_bw = np.roll(res_bw, -kw//2, 1)

        res_bw = np.uint8(res_bw / np.amax(res_bw) * 255.0)

        # self.imageCV = res_bw
        self.latestFunction = self.deconvolve
        self.update(res_bw)

    def update(self, image):
        """Update the image view
        """
        if self.isColor(image):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imFormat = QImage.Format_RGB888
            # print "Colour", imFormat
            numBytes = 3
        else:
            imFormat = QImage.Format_Grayscale8
            # print "Grayscale", imFormat
            numBytes = 1

        image = QImage(image.data, image.shape[1], image.shape[0],
                image.shape[1] * numBytes, imFormat)
        pixMap = QPixmap(image)

        self.item.setPixmap(pixMap)

    def isColor(self, image):
        return len(image.shape) == 3 and image.shape[2] == 3


class ImageEditorWindow(QMainWindow):
    """Window to house image editor
    """
    def __init__(self, mainWindow=None):
        super(ImageEditorWindow, self).__init__(mainWindow)
        self.setWindowTitle("Image Editor")
        self.setWindowIcon(QIcon("ui/astro.png"))
        self.resize(742, 540)
        self.showing = False
        self.editor = ImageEditor()
        self.setCentralWidget(self.editor)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.showing = False
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageEditorWindow()
    window.show()
    window.editor.showImage("v282.jpeg")
    sys.exit(app.exec_())
