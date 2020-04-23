import os
import logging
import numpy as np
import audiofile as af
import ffmpeg
import pygame
import time
from scipy import signal
from scipy.signal import butter, lfilter
from matplotlib import pyplot as plt

import yaml
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from generated import mainWindow_ui
from util import constants, util
from util.fileDialog import FileDialog

logger = logging.getLogger(__name__)

# class for main window of UI
class MainWindow(QMainWindow, mainWindow_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setDefaults()
        self.loadSettings()

        self.ctl = " "
        self.ctl2 = " "
        self.filenameData = " "
        self.filename = " "
        self.fs = 44100
        self.sig = 0
        self.order = 5

        nyq = 0.5 * self.fs
        self.high1 = self.highcut1 / nyq
        self.b1, self.a1 = signal.butter(self.order, self.high1, 'low')
        self.filteredSig1 = lfilter(self.b1, self.a1, self.sig, axis=-1)
        self.filteredSig1 = self.gainSlider_band1.value() / 100 * self.filteredSig1

        nyq = 0.5 * self.fs
        self.low2 = self.lowcut2 / nyq
        self.high2 = self.highcut2 / nyq
        self.b2, self.a2 = signal.butter(self.order, [self.low2, self.high2], btype='bandpass')
        self.filteredSig2 = lfilter(self.b2, self.a2, self.sig, axis=-1)
        self.filteredSig2 = self.gainSlider_band2.value() / 100 * self.filteredSig2

        nyq = 0.5 * self.fs
        self.low3 = self.lowcut3 / nyq
        self.high3 = self.highcut3 / nyq
        self.b3, self.a3 = butter(self.order, [self.low3, self.high3], btype='bandpass')
        self.filteredSig3 = lfilter(self.b3, self.a3, self.sig, axis=-1)
        self.filteredSig3 = self.gainSlider_band3.value() / 100 * self.filteredSig3

        nyq = 0.5 * self.fs
        self.low4 = self.lowcut4 / nyq
        self.high4 = self.highcut4 / nyq
        self.b4, self.a4 = butter(self.order, [self.low4, self.high4], btype='bandpass')
        self.filteredSig4 = lfilter(self.b4, self.a4, self.sig, axis=-1)
        self.filteredSig4 = self.gainSlider_band4.value() / 100 * self.filteredSig4

        self.highcut5 = 20000
        nyq = 0.5 * self.fs
        self.low5 = self.lowcut5 / nyq
        self.high5 = self.highcut5 / nyq
        self.b5, self.a5 = butter(self.order, [self.low5, self.high5], btype='high')
        self.filteredSig5 = lfilter(self.b5, self.a5, self.sig, axis=-1)
        self.filteredSig5 = self.gainSlider_band5.value() / 100 * self.filteredSig5

        self.newSig = pygame.mixer.sound(
        self.filteredSig1 + self.filteredSig2 + self.filteredSig3 + self.filteredSig4 + self.filteredSig5)

    def loadSettings(self):
        settings = QSettings(constants.applicationName, constants.organizationName)
        settings.beginGroup('Equalizer')

        geometry = settings.value('geometry', QByteArray(), type=QByteArray)
        if not geometry.isEmpty():
            self.restoreGeometry(geometry)

            # Fixes QTBUG-46620 issue
            if settings.value('maximized', False, type=bool):
                self.showMaximized()
                self.setGeometry(QApplication.desktop().availableGeometry(self))

        # default path
        self.defaultOpenPath = settings.value('defaultOpenPath', QDir.homePath(), type=str)

        settings.endGroup()


    def saveSettings(self):
        settings = QSettings(constants.applicationName, constants.organizationName)
        settings.beginGroup('Equalizer')

        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('maximized', self.isMaximized())
        settings.setValue('defaultOpenPath', self.defaultOpenPath)

        settings.endGroup()


    def setDefaults(self):
        self.gainLabel1.setText('Band 1 Gain: 100%')
        self.gainLabel2.setText('Band 2 Gain: 100%')
        self.gainLabel3.setText('Band 3 Gain: 100%')
        self.gainLabel4.setText('Band 4 Gain: 100%')
        self.gainLabel5.setText('Band 5 Gain: 100%')
        self.lowcut2 = 300
        self.lowcut3 = 1000
        self.lowcut4 = 2500
        self.lowcut5 = 5000
        self.highcut1 = 299
        self.highcut2 = 999
        self.highcut3 = 2499
        self.highcut4 = 4999
        self.leftCutLabel2.setText("300 Hz")
        self.leftCutLabel3.setText("1000 Hz")
        self.leftCutLabel4.setText("2500 Hz")
        self.leftCutLabel5.setText("5000 Hz")
        self.rightCutLabel1.setText("299 Hz")
        self.rightCutLabel2.setText("999 Hz")
        self.rightCutLabel3.setText("2499 Hz")
        self.rightCutLabel4.setText("4999 Hz")

        pygame.init()
        pygame.mixer.init()


    @pyqtSlot(int)
    def on_gainSlider_band1_valueChanged(self, value):
        self.gainLabel1.setText('Band 1 Gain: %d' % value + '%')
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_gainSlider_band2_valueChanged(self, value):
        self.gainLabel2.setText('Band 2 Gain: %d' % value + '%')
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_gainSlider_band3_valueChanged(self, value):
        self.gainLabel3.setText('Band 3 Gain: %d' % value + '%')
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_gainSlider_band4_valueChanged(self, value):
        self.gainLabel4.setText('Band 4 Gain: %d' % value + '%')
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_gainSlider_band5_valueChanged(self, value):
        self.gainLabel5.setText('Band 5 Gain: %d' % value + '%')
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_rightCutSlider_band1_valueChanged(self, value):
        self.rightCutLabel1.setText('Band 1 Right Cutoff: %d' % value + ' Hz')
        self.highcut1 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_leftCutSlider_band2_valueChanged(self, value):
        self.leftCutLabel2.setText('Band 2 Left Cutoff: %d' % value + ' Hz')
        self.lowcut2 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_rightCutSlider_band2_valueChanged(self, value):
        self.rightCutLabel2.setText('Band 2 Right Cutoff: %d' % value + ' Hz')
        self.highcut2 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_leftCutSlider_band3_valueChanged(self, value):
        self.leftCutLabel3.setText('Band 3 Left Cutoff: %d' % value + ' Hz')
        self.lowcut3 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_rightCutSlider_band3_valueChanged(self, value):
        self.rightCutLabel3.setText('Band 3 Right Cutoff: %d' % value + ' Hz')
        self.highcut3 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot(int)
    def on_leftCutSlider_band4_valueChanged(self, value):
        self.leftCutLabel4.setText('Band 4 Left Cutoff: %d' % value + ' Hz')
        self.lowcut4 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "


    def on_rightCutSlider_band4_valueChanged(self, value):
        self.rightCutLabel4.setText('Band 4 Right Cutoff: %d') % value + ' Hz'
        self.highcut4 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    def on_leftCutSlider_band5_valueChanged(self, value):
        self.leftCutLabel5.setText('Band 5 Left Cutoff: %d' % value + ' Hz')
        self.lowcut5 = value
        if (self.ctl or self.ctl2) == "play":
            pygame.mixer.music.stop()
            self.ctl = " "
            self.ctl2 = " "

    @pyqtSlot()
    def on_uploadAudio_clicked(self):
        self.fullPath, filterReturn = FileDialog.getOpenFileName(self, 'Select .wav file', self.defaultOpenPath, '*.wav')
        print(self.fullPath)
        self.filenameData = util.splitext((os.path.basename(self.fullPath)))
        self.filename = self.filenameData[0] + self.filenameData[1]
        print('Audio File Grabbed: ' + self.filename)
        self.audioLabel.setText('Audio File: ' + self.filename)
        self.sig, self.fs = af.read(self.filename)
        pygame.mixer.music.load(self.sig)
        print('Original Sampling Rate: ' + str(self.fs) + ' Hz')
        self.fsLabel.setText('Original Sampling Rate: ' + str(self.fs) + ' Hz')

    @pyqtSlot()
    def on_playButton_clicked(self):
        if self.ctl == " ":
            self.ctl = "play"
            print("start play")
            pygame.mixer.music.play(0)
        elif self.ctl == "paused":
            self.ctl = "play"
            print("resume play")
            pygame.mixer.music.unpause()

    @pyqtSlot()
    def on_pauseButton_clicked(self):
        self.ctl2 = "paused"
        print(self.ctl2)
        pygame.mixer.music.pause()

    @pyqtSlot()
    def on_stopButton_clicked(self):
        self.ctl2 = " "
        print("stopped")
        pygame.mixer.music.stop()

    @pyqtSlot(int)
    def on_playButton_2_clicked(self):
        if self.ctl2 == " ":
            self.ctl2 = "play"
            print("start play")
            pygame.mixer.music.load(self.newSig)
            pygame.mixer.music.play(0)
        elif self.ctl == "paused":
            self.ctl = "play"
            print("resume play")
            pygame.mixer.music.unpause()

    @pyqtSlot()
    def on_pauseButton_2_clicked(self):
        self.ctl = "paused"
        print(self.ctl)
        pygame.mixer.music.pause()

    @pyqtSlot()
    def on_stopButton_2_clicked(self):
        self.ctl = " "
        print("stopped")
        pygame.mixer.music.stop()






















