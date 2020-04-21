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
        self.filenameData = " "
        self.filename = " "
        self.fs = 0
        self.sig = 0
        self.order = 5

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
        self.gainSlider_band1.setValue(100)
        self.gainSlider_band2.setValue(100)
        self.gainSlider_band3.setValue(100)
        self.gainSlider_band4.setValue(100)
        self.gainSlider_band5.setValue(100)
        self.gainSlider_band1.setMinimum(0)
        self.gainSlider_band1.setMaximum(100)
        self.gainSlider_band2.setMinimum(0)
        self.gainSlider_band2.setMaximum(100)
        self.gainSlider_band3.setMinimum(0)
        self.gainSlider_band3.setMaximum(100)
        self.gainSlider_band4.setMinimum(0)
        self.gainSlider_band4.setMaximum(100)
        self.gainSlider_band5.setMinimum(0)
        self.gainSlider_band5.setMaximum(100)
        self.gainLabel1.setText('Band 1 Gain: 100%')
        self.gainLabel2.setText('Band 2 Gain: 100%')
        self.gainLabel3.setText('Band 3 Gain: 100%')
        self.gainLabel4.setText('Band 4 Gain: 100%')
        self.gainLabel5.setText('Band 5 Gain: 100%')
        pygame.init()
        pygame.mixer.init()



    @pyqtSlot(int)
    def on_gainSlider_band1_valueChanged(self, value):
        self.gainLabel1.setText('Band 1 Gain: %d' % value + '%')


    @pyqtSlot(int)
    def on_gainSlider_band2_valueChanged(self, value):
        self.gainLabel2.setText('Band 2 Gain: %d' % value + '%')


    @pyqtSlot(int)
    def on_gainSlider_band3_valueChanged(self, value):
        self.gainLabel3.setText('Band 3 Gain: %d' % value + '%')


    @pyqtSlot(int)
    def on_gainSlider_band4_valueChanged(self, value):
        self.gainLabel4.setText('Band 4 Gain: %d' % value + '%')


    @pyqtSlot(int)
    def on_gainSlider_band5_valueChanged(self, value):
        self.gainLabel5.setText('Band 5 Gain: %d' % value + '%')


    def on_rightCutSlider_band1_valueChanged(self, value):
        self.rightCutLabel1.setText('Band 1 Right Cutoff: %d' % value + ' Hz')
        self.highcut1 = value


    def on_leftCutSlider_band2_valueChanged(self, value):
        self.leftCutLabel2.setText('Band 2 Left Cutoff: %d' % value + ' Hz')
        self.lowcut2 = value


    def on_rightCutSlider_band2_valueChanged(self, value):
        self.rightCutLabel2.setText('Band 2 Right Cutoff: %d' % value + ' Hz')
        self.highcut2 = value


    def on_leftCutSlider_band3_valueChanged(self, value):
        self.leftCutLabel3.setText('Band 3 Left Cutoff: %d' % value + ' Hz')
        self.lowcut3 = value


    def on_rightCutSlider_band3_valueChanged(self, value):
        self.rightCutLabel3.setText('Band 3 Right Cutoff: %d' % value + ' Hz')
        self.highcut3 = value


    def on_leftCutSlider_band4_valueChanged(self, value):
        self.leftCutLabel4.setText('Band 4 Left Cutoff: %d' % value + ' Hz')
        self.lowcut4 = value


    def on_rightCutSlider_band4_valueChanged(self, value):
        self.rightCutLabel4.setText('Band 4 Right Cutoff: %d') % value + ' Hz'
        self.highcut4 = value


    def on_leftCutSlider_band5_valueChanged(self, value):
        self.leftCutLabel5.setText('Band 5 Left Cutoff: %d' % value + ' Hz')
        self.lowcut5 = value


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
        self.ctl = "paused"
        print(self.ctl)
        pygame.mixer.music.pause()

    @pyqtSlot()
    def on_stopButton_clicked(self):
        self.ctl = " "
        print("stopped")
        pygame.mixer.music.stop()

    def eq_5band(self):
        self.lowcut1 = 0

        nyq = 0.5 * self.fs
        self.low1 = self.lowcut1 / nyq
        self.high1 = self.highcut1 / nyq
        self.b1, self.a1 = butter(self.order, [self.low1, self.high1], btype='bandpass')
        self.filteredSig1 = lfilter(self.b1, self.a1, self.sig)
        self.filteredSig1 = self.gainSlider_band1.value() / 100 * self.filteredSig1

        nyq = 0.5 * self.fs
        self.low2 = self.lowcut2 / nyq
        self.high2 = self.highcut2 / nyq
        self.b2, self.a2 = butter(self.order, [self.low2, self.high2], btype='bandpass')
        self.filteredSig2 = lfilter(self.b2, self.a2, self.sig)
        self.filteredSig2 = self.gainSlider_band2.value() / 100 * self.filteredSig2

        nyq = 0.5 * self.fs
        self.low3 = self.lowcut3 / nyq
        self.high3 = self.highcut3 / nyq
        self.b3, self.a3 = butter(self.order, [self.low3, self.high3], btype='bandpass')
        self.filteredSig3 = lfilter(self.b3, self.a3, self.sig)
        self.filteredSig3 = self.gainSlider_band3.value() / 100 * self.filteredSig3

        nyq = 0.5 * self.fs
        self.low4 = self.lowcut4 / nyq
        self.high4 = self.highcut4 / nyq
        self.b4, self.a4 = butter(self.order, [self.low4, self.high4], btype='bandpass')
        self.filteredSig4 = lfilter(self.b4, self.a4, self.sig)
        self.filteredSig4 = self.gainSlider_band4.value() / 100 * self.filteredSig4

        self.highcut5 = 20000
        nyq = 0.5 * self.fs
        self.low5 = self.lowcut5 / nyq
        self.high5 = self.highcut5 / nyq
        self.b5, self.a5 = butter(self.order, [self.low5, self.high5], btype='bandpass')
        self.filteredSig5 = lfilter(self.b5, self.a5, self.sig)
        self.filteredSig5 = self.gainSlider_band5.value() / 100 * self.filteredSig5

        self.newSig = self.filteredSig1 + self.filteredSig2 + self.filteredSig3 + self.filteredSig4 + self.filteredSig5





















