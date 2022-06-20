"""
imageSelector.py

Widget to display and navigate saved images.
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
from imageEditor import ImageEditorWindow
from conf.settings import GC_Settings, MSG_Settings


class ImageSelector(QWidget):

    def __init__(self, mainWindow, imageDirectory):

        super(ImageSelector, self).__init__(mainWindow)

        self.current = 0
        self.max = -1 # TODO
        self.imageFilename = None
        self.imageDirectory = imageDirectory
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")

        self.image = QLabel("No image to show")
        self.imageEditorWindow = ImageEditorWindow(mainWindow)
        self.image.mouseDoubleClickEvent = self.showImageInEditor

        self.btnNext = QPushButton("<")
        self.btnNext.clicked.connect(self.nextImage)
        self.imageName = QLabel("No image files")
        self.btnPrev = QPushButton(">")
        self.btnPrev.clicked.connect(self.prevImage)

        self.layout.addWidget(self.image, 0, 0, 1, 3, Qt.AlignCenter)
        self.layout.addWidget(self.btnNext, 1, 0)
        self.layout.addWidget(self.imageName, 1, 1, Qt.AlignCenter)
        self.layout.addWidget(self.btnPrev, 1, 2)

        self.imageFilenames = []

        # self.imageDirectory = "18-05-11-10-48-39" # TODO
        # self.showImage("18-05-11-10-48-39/h0.jpeg") # TODO
        # self.showImage(self.imageDirectory + "/h0.jpeg") # TODO

    def showImage(self, filename, new=False):
        pm = QPixmap(os.path.abspath("images/" + filename).replace("\\","/"))
        pm2 = pm.scaledToHeight(min(300, max(200, self.image.height())))
        self.image.setPixmap(pm2)
        self.imageFilename = filename
        self.imageName.setText(filename.split("/")[-1])
        if new:
            self.max += 1
            self.current = self.max
            self.imageFilenames.append(filename.split("/")[-1])

    def showImageInEditor(self, event):
        if not self.imageEditorWindow.showing:
            self.imageEditorWindow.show()
            self.imageEditorWindow.showing = True
            self.imageEditorWindow.move(20, 20)
        if self.imageFilename is not None:
            self.imageEditorWindow.editor.showImage(self.imageFilename)

    def nextImage(self):
        if self.current < self.max and MSG_Settings.IMAGE_EXT \
                in self.imageFilenames[self.current + 1]:
            self.showImage(self.imageDirectory + "/" + \
                    self.imageFilenames[self.current + 1])
            self.current += 1

    def prevImage(self):
        if self.current > 0 and MSG_Settings.IMAGE_EXT \
                in self.imageFilenames[self.current - 1]:
            self.showImage(self.imageDirectory + "/" + \
                    self.imageFilenames[self.current - 1])
            self.current -= 1
