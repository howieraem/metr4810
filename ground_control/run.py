"""
run.py

The main program for the ground control interface (GC).
Manages communication with the telescope (TS).
"""

import sys
import os
sys.path.append(os.path.abspath('..//')) # to import from other directories
import serial
import time
from concurrent.futures import ThreadPoolExecutor
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtCore, QtGui
from ui.customUI import Ui_MainWindow
from telescopeLink import TelescopeLink
from transmitter import Transmitter
from dataManager import DataManager
from dummySerial import DummySerial
from unityManager import UnityManager
from conf.settings import GC_Settings
import winWifi


class MainWindow(QMainWindow):
    """The main window for the Ground Control Interface
    """
    EXIT_CODE_REBOOT = -123

    def __init__(self):
        """Constructor
        """
        super(MainWindow, self).__init__()
        # Set up data handlers and UI
        self.dm = DataManager()
        if GC_Settings.USE_DSN:
            serialLink = serial.Serial(GC_Settings.DSN_PORT, 
                    baudrate=GC_Settings.DSN_BAUD)
        else:
            serialLink = DummySerial()
        self.tl = TelescopeLink(serialLink)
        self.tx = Transmitter(serialLink)
        self.um = None # UnityManager()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.dm.image_directory)
        self.ui.setupSwitches(self.eStop, self.restart)
        self.setWindowIcon(QtGui.QIcon("images/astro.png"))

        # Set up threading
        self.pool = ThreadPoolExecutor(5)
        self.imgFuture = None
        # Threading manageData() requires signals/slots for UI updates
        # so do not use in this threading strategy
        # self.dataFuture = self.pool.submit(self.manageData, (0))

        # Timer pausing GUI to run other code regularly
        # GUI will hang during long continuous operations
        self.msgTime = time.time() # Time of last message received from TS
        self.timer = QtCore.QTimer()
        self.timer.stop
        self.timer.timeout.connect(self.manageData)

        # Check for connection (used when GC is access point)
        # while not self.tl.connection():
        #     continue
        # self.ui.update_status("av")

        self.timer.start(0) # milliseconds

    def manageData(self):
        """Manage incoming and outgoing data between GC and TS
        """

        # while not GC_Settings.quit:
        # print "man"
        # The telescope's "busy" message disables commands.
        # Just in case we miss the "ready" message,
        # reenable commands after some time.
        # if time.time() - self.msgTime > GC_Settings.MSG_TIMEOUT:
        #     self.ui.reset()

        # Check for data to send to DSN (i.e. command)
        if self.dm.msg_ready:
            if not self.groundCmd(self.dm.msg):
                self.tl.send_msg(self.dm.msg)
            self.dm.msg_sent()
        if self.dm.image_ready:
            self.dm.image_received()
            self.ui.statusbarGC.showMessage("GC: Receiving image...")
            # Start thread for receiving image
            self.imgFuture = self.pool.submit(self.tl.receive_hd, 
                    (self.dm.image_filename))
        if self.dm.program_ready:
            self.tl.send_hex_file()
            self.dm.programming_done()

        # Check for message from DSN
        self.tx.send_if_ready()

        if self.imgFuture is not None and self.imgFuture.done():
            # Finished receiving
            if self.imgFuture.result(): 
                # Successful
                self.ui.imageSelector.showImage(
                        self.dm.image_filename, new=True)
                self.ui.statusbarGC.showMessage(
                        "GC: Receiving image...done")
            else:
                self.ui.statusbarGC.showMessage(
                        "GC: Receiving image...fail")
            self.imgFuture = None

        if self.ui.videoFeedCV.frameReady:
            # Pull a frame from the video feed
            self.dm.name_image("v")
            self.ui.videoFeedCV.getFrame(
                    self.dm.image_filename)
            self.ui.imageSelector.showImage(
                    self.dm.image_filename, new=True)
            self.ui.statusbarGC.showMessage(
                    "GC: Pulled image from video")

        # Data from telescope
        ts_msg = self.tl.receive_msg()
        if ts_msg is not None:
            # print "TS message = ", ts_msg
            accepted, key, data = self.dm.interpret_in_bin(ts_msg)
            if accepted:
                # self.msgTime = time.time()
                self.handleMessage(key, data)

        # Check again for data to telescope (i.e. reply)
        if self.dm.msg_ready:
            if not self.groundCmd(self.dm.msg):
                self.tl.send_msg(self.dm.msg)
            self.dm.msg_sent()

    def groundCmd(self, cmd):
        """Check if a command is just for ground
        """
        key = cmd[1]
        if key == "w":
            # Wifi data from ground (when Pi is access point)
            wifiData = winWifi.get_info()
            if wifiData is None:
                data = ("-", "-")
            else:
                data = wifiData
            self.ui.update_readings(key, data)
            return True
        return False

    def handleMessage(self, key, data):
        """Direct message data to different UI elements
        """
        if self.dm.reply_received:
            self.ui.console.insertEnd("TS: " + self.dm.reply_from_ts)
            self.ui.update_status(self.dm.reply_from_ts[:1])
            self.dm.reply_printed()
        elif self.dm.readings_received:
            self.ui.update_readings(key, data)
            if self.um is not None:
                self.um.send(key, data)
            if key == 'r':
                # Update video rotation compensation
                self.ui.videoFeedCV.roll = int(float(data[0]))
            self.dm.readings_printed()
        elif self.dm.status_received:
            if key == 'y':
                # Special case - image transmitted without request
                pass
                # self.dm.name_image('h') # TODO
                # self.dm.image_ready = True
            self.ui.update_status(key)
            self.dm.status_printed()
        else:
            print "Did not recognise message"

    def prepareCommand(self):
        """Prepare a command message to be sent
        """
        # Retrieve command from UI
        command = self.ui.commandLine.enterCommand()
        # Fix and validate format
        if command is not None:
            if command[0] != "$":
                command = "$" + command
            if command[-1] != "\n":
                command += "\n"
            if self.ui.commandLine.enable:
                accepted = self.dm.interpret_out(command)
                self.ui.console.commandReport(accepted)
            else:
                self.ui.console.commandReject()

    def orientDC(self, dc):
        self.ui.commandLine.setText("o{},{}".format(
                self.dm.dc + dc, self.dm.ra))
        self.prepareCommand()

    def orientRA(self, ra):
        """Convenience function to change telescope right ascension
        """
        self.ui.commandLine.setText("o{},{}".format(
                self.dm.dc, self.dm.ra + ra))
        self.prepareCommand()

    def orientRoll(self, roll):
        """Convenience function to change telescope roll reference
        """
        self.ui.commandLine.setText("r{}".format(
                self.ui.videoFeedCV.roll + roll))
        self.prepareCommand()

    def eStop(self):
        """Convenience function to send stop command
        """
        self.ui.commandLine.setText("s0")
        self.prepareCommand()

    def restart(self):
        """Convenience function to send start command
        """
        self.ui.commandLine.setText("s1")
        self.prepareCommand()
        self.dm.dc = 0.0
        self.dm.ra = 0.0

    def keyPressEvent(self, e):
        """Handle key press for UI commands
        """
        cmdFocus = self.ui.commandLine.hasFocus()
        # Ctrl + ...
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            if (e.modifiers() & QtCore.Qt.ShiftModifier):
                if e.key() == QtCore.Qt.Key_R:
                    self.rebootChoice()
            if e.key() == QtCore.Qt.Key_E:
                if cmdFocus:
                    self.ui.commandLine.clearFocus()
                else:
                    self.ui.commandLine.setFocus()
        if cmdFocus:
            if e.key() == QtCore.Qt.Key_Return:
                self.prepareCommand()
            if e.key() == QtCore.Qt.Key_Escape:
                self.ui.commandLine.clearFocus()
        else:
            if e.key() == QtCore.Qt.Key_W:
                self.orientDC(self.dm.ocsIncrement)
            if e.key() == QtCore.Qt.Key_S:
                self.orientDC(-self.dm.ocsIncrement)
            if e.key() == QtCore.Qt.Key_D:
                self.orientRA(self.dm.ocsIncrement)
            if e.key() == QtCore.Qt.Key_A:
                self.orientRA(-self.dm.ocsIncrement)
            if e.key() == QtCore.Qt.Key_V:
                self.ui.videoFeedCV.toggleDisplay()
            if e.key() == QtCore.Qt.Key_R:
                self.ui.videoFeedCV.prepareFrame()
            if e.key() == QtCore.Qt.Key_F:
                self.ui.imageSelector.nextImage()
            if e.key() == QtCore.Qt.Key_G:
                self.ui.imageSelector.prevImage()
            if e.key() == QtCore.Qt.Key_H:
                self.orientRoll(-self.dm.rollIncrement)
            if e.key() == QtCore.Qt.Key_J:
                self.orientRoll(self.dm.rollIncrement)

    def packDown(self):
        """Procedure for closing the program
        """
        GC_Settings.quit = True
        self.tl.close()

        def kill_proc_tree(pid, including_parent=True):    
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            if including_parent:
                parent.kill()
                parent.wait(5)

        me = os.getpid()
        kill_proc_tree(me, False)

    def closeEvent(self, e):
        """Override to customise close procedure
        """
        self.packDown()
        time.sleep(0.1)
        e.accept()

    def rebootChoice(self):
        """Prompt the user to reboot the application
        """
        choice = QMessageBox.question(self, "Reboot",
                "Reboot application?",
                QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.reboot()
        else:
            pass

    def reboot(self):
        """Reboot the application, restoring initial state
        """
        self.packDown()
        time.sleep(0.1)
        QApplication.exit(MainWindow.EXIT_CODE_REBOOT)


if __name__ == '__main__':
    # Keep executing the main Qt application as long as it exits
    # with the reboot signal, otherwise end the program.
    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        a = QApplication(sys.argv)
        w = MainWindow()
        w.show()
        currentExitCode = a.exec_()
        a = None  # delete the QApplication object
