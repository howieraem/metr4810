"""
customUI.py

Constructs and manages the user interface.
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from command import Console, CommandLine
from imageFeed import VideoFeedCV
from imageEditor import ImageEditorWindow
from imageSelector import ImageSelector

import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
from conf.settings import GC_Settings


class Ui_MainWindow(object):

    def __init__(self):
        pass

    def setupUi(self, MainWindow, imageDirectory):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(742, 540)

        self.cmdWidget = QtWidgets.QWidget()
        self.cmdLayout = QtWidgets.QVBoxLayout(self.cmdWidget)
        self.cmdLayout.setContentsMargins(0, 0, 0, 0)
        self.cmdLayout.setObjectName("cmdLayout")
        self.console = Console()
        self.commandLine = CommandLine(self.console)
        self.cmdLayout.addWidget(self.console)
        self.cmdLayout.addWidget(self.commandLine)

        self.videoWidget = QtWidgets.QWidget()
        self.videoLayout = QtWidgets.QHBoxLayout(self.videoWidget)
        self.videoFeedCV = VideoFeedCV()
        self.videoLayout.addWidget(self.videoFeedCV.button)
        self.videoLayout.addWidget(self.videoFeedCV.btnReset)
        # self.videoLayout.addWidget(self.videoFeedCV.btnReset)

        self.setupTelemetry()

        self.imageSelector = ImageSelector(MainWindow, imageDirectory)
        self.switchWidget = QtWidgets.QWidget()
        self.switchLayout = QtWidgets.QHBoxLayout(self.switchWidget)
        self.btnEStop = QtWidgets.QPushButton("STOP")
        self.btnEStop.setStyleSheet("background-color: red")
        self.switchLayout.addWidget(self.btnEStop)
        self.btnRestart = QtWidgets.QPushButton("START")
        self.btnRestart.setStyleSheet("background-color: green")
        self.switchLayout.addWidget(self.btnRestart)

        self.mainLayout = QtWidgets.QGridLayout()
        topWidgets = [self.cmdWidget, self.imageSelector,
                self.videoWidget, self.telemetryWidget, self.switchWidget]
        positions = [
                [(0, 0), (1, 2)], 
                [(1, 0), (1, 2)],
                [(2, 0), (1, 2)],
                [(0, 2), (2, 1)],
                [(2, 2), (1, 1)]]
        for w, p in zip(topWidgets, positions):
            self.mainLayout.addWidget(w, p[0][0], p[0][1], p[1][0], p[1][1])

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setLayout(self.mainLayout)

        self.toolbar = QtWidgets.QToolBar("maintoolbar")
        MainWindow.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
        self.statusbarGC = QtWidgets.QStatusBar()
        self.statusbarGC.showMessage("GC: Ready")
        self.toolbar.addWidget(self.statusbarGC)
        self.statusbarTS = QtWidgets.QStatusBar()
        self.statusbarTS.showMessage("TS: Waiting to initialise")
        self.toolbar.addWidget(self.statusbarTS)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 742, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.actionFile = QtWidgets.QAction(MainWindow)
        self.actionFile.setObjectName("actionFile")

        self.retranslateUi(MainWindow)
        self.applyStyle(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setupTelemetry(self):
        self.telemetryWidget = QtWidgets.QWidget()
        self.telemetryWidget.setObjectName("telemetryWidget")
        self.telemetryLayout = QtWidgets.QGridLayout(self.telemetryWidget)
        self.telemetryLayout.setHorizontalSpacing(30)
        # self.telemetryLayout.setContentsMargins(0, 0, 0, 0)
        self.telemetryLayout.setObjectName("telemetryLayout")
        self.gyroNames = [QtWidgets.QLabel("Gyro" + i + " (deg)") for i in (\
                'X', 'Y', 'Z')]
        self.rateNames = [QtWidgets.QLabel("Rate" + i + " (dps)") for i in (\
                'X', 'Y', 'Z')]
        self.elecNames = [QtWidgets.QLabel(i) for i in (\
                'Ix (A)', 'Vbat (V)')]
        # self.sgnlNames = [QtWidgets.QLabel(i) for i in (\
        #         'Bitrate (Mbps)', 'Link quality (%)', 'Signal level (dBm)')]
        self.sgnlNames = [QtWidgets.QLabel(i) for i in (\
                'Bitrate (Mbps)', 'Signal (%)')]
        self.gyroVals = [QtWidgets.QLabel("-") for i in range(3)]
        self.rateVals = [QtWidgets.QLabel("-") for i in range(3)]
        self.elecVals = [QtWidgets.QLabel("-") for i in range(2)]
        self.sgnlVals = [QtWidgets.QLabel("-") for i in range(2)]

        self.statDict = {'r': self.gyroVals,
                         'f': self.rateVals,
                         'v': self.elecVals,
                         'w': self.sgnlVals,
                        } # for setting values received from telescope
        self.telemetrySet = [[self.gyroNames, self.gyroVals],
                             [self.rateNames, self.rateVals],
                             [self.elecNames, self.elecVals],
                             [self.sgnlNames, self.sgnlVals],
                            ]
        telemetryFont = QtGui.QFont()
        telemetryFont.setFamily("Consolas")
        telemetryFont.setPointSize(12)
        row = 0
        for i, name_val in enumerate(self.telemetrySet):
            for j, name in enumerate(name_val[0]):
                name.setFont(telemetryFont)
                self.telemetryLayout.addWidget(name, row, 0)
                name_val[1][j].setFont(telemetryFont)
                name_val[1][j].setMinimumWidth(75)
                name_val[1][j].setMaximumWidth(75)
                self.telemetryLayout.addWidget(name_val[1][j], row, 1)
                row += 1

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", 
                "John Tebutt Space Telescope Ground Control"))
        self.actionFile.setText(_translate("MainWindow", "File"))

    def update_readings(self, key, data):
        # Data manager has handled validation
        # Example: key = 'r', data = ['23.25', '-13.92']
        # print "Updating readings"
        for i in range(len(data)):
            self.statDict[key][i].setText(data[i])

    def setupSwitches(self, eStopFcn, restartFcn):
        self.btnEStop.clicked.connect(eStopFcn)
        self.btnRestart.clicked.connect(restartFcn)

    def update_status(self, key):
        # Data manager has handled validation
        # Disable command acceptance
        if key == "b":
            self.commandLine.enable = False
            self.statusbarTS.showMessage("TS: Busy")
        elif key == "s":
            self.commandLine.enable = True
            self.statusbarTS.showMessage("TS: Ready")
        elif key == "y":
            self.statusbarTS.showMessage("TS: Image")
        elif key == "av": # Only within ground control
            self.statusbarTS.showMessage("TS: Available")
        elif key == "t":
            self.statusbarTS.showMessage("TS: Ready")

    def reset(self):
        self.commandLine.enable = True

    def applyStyle(self, mw):
        mw.setStyleSheet(
            ".QWidget#telemetryWidget {border: 1px solid rgb(125,125,116);}")
