"""
command.py

Widgets for the messaging interface
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QFont, QTextCursor


class Console(QPlainTextEdit):

    def __init__(self):
        super(Console, self).__init__()
        # TODO: Use signals and slots to block access
        # self.setGeometry(QRect(240, 10, 481, 121))
        self.setReadOnly(True)
        self.setPlainText("")
        self.setObjectName("console")
        default_font = QFont()
        default_font.setFamily("Consolas")
        default_font.setPointSize(12)
        self.setFont(default_font)
        self.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)

        self.insertEnd(" Ground Control\n---------------------\n")
        # self.insertEnd("GC: Ready\n")

    def scrollToBottom(self):
        if self.verticalScrollBar().maximum() \
                - self.verticalScrollBar().value() < 2:
            self.verticalScrollBar().setSliderPosition(
                    self.verticalScrollBar().maximum())

    def insertEnd(self, text, keepScroll=True):
        # Note the current scroll position
        scrollRatio = 1
        if keepScroll and self.verticalScrollBar().maximum() > 0:
            scrollRatio = self.verticalScrollBar().value() \
                    / float(self.verticalScrollBar().maximum())

        # Insert the new text
        if text[-1] != "\n":
            text += "\n"
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)

        # Return to initial scroll position
        if keepScroll and self.verticalScrollBar().maximum() > 0:
            self.verticalScrollBar().setSliderPosition(
                    int(scrollRatio * self.verticalScrollBar().maximum()))
        self.scrollToBottom() # autoscroll if it is near the bottom

    def tEchoCommand(self, command):
        return lambda: self.echoCommand(command)

    def echoCommand(self, command):
        self.insertEnd(">>> " + command + "\n")

    def commandReport(self, accepted):
        if accepted:
            self.insertEnd("GC: command sent\n")
        else:
            self.insertEnd("GC: command not recognised\n")

    def commandReject(self):
        self.insertEnd("GC: command rejected (TS is busy)\n")


class CommandLine(QLineEdit):

    def __init__(self, console):
        super(CommandLine, self).__init__()
        self.console = console
        self.enable = True
        # self.setGeometry(QRect(240, 140, 401, 20))
        self.setText("")
        self.setObjectName("commandLine")
        default_font = QFont()
        default_font.setFamily("Consolas")
        default_font.setPointSize(12)
        self.setFont(default_font)

    def enterCommand(self):
        focus = self.hasFocus()
        command = self.text()
        print "Command: ", command
        if len(command) > 0:
            self.console.echoCommand(command)
            self.clear()
            if focus:
                self.setFocus()
            return command
        return None
 

