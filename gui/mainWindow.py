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
        self.order = 5
        self.nyq = 0.5 * self.fs

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
        self.leftCutLabel2.setText("Band 2 Left Cutoff: 300 Hz")
        self.leftCutLabel3.setText("Band 3 Left Cutoff: 1000 Hz")
        self.leftCutLabel4.setText("Band 4 Left Cutoff: 2500 Hz")
        self.leftCutLabel5.setText("Band 5 Left Cutoff: 5000 Hz")
        self.rightCutLabel1.setText("Band 1 Right Cutoff: 299 Hz")
        self.rightCutLabel2.setText("Band 2 Right Cutoff: 999 Hz")
        self.rightCutLabel3.setText("Band 3 Right Cutoff: 2499 Hz")
        self.rightCutLabel4.setText("Band 4 Right Cutoff: 4999 Hz")

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

    def eq_5band(self):
        nyq = 0.5 * self.fs

        self.highcut1 = self.highcut1 / nyq
        b1, a1 = signal.butter(5, self.highcut1, 'low')
        w1, h1 = signal.freqz(b1, a1)

        self.lowcut2 = self.lowcut2 / nyq
        self.highcut2 = self.highcut2 / nyq
        b2, a2 = signal.butter(4, [self.lowcut2, self.highcut2], 'bandpass')
        w2, h2 = signal.freqz(b2, a2)

        self.lowcut3 = self.lowcut3 / nyq
        self.highcut3 = self.highcut3 / nyq
        b3, a3 = signal.butter(7, [self.lowcut3, self.highcut3], 'bandpass')
        w3, h3 = signal.freqz(b3, a3)

        self.lowcut4 = self.lowcut4 / nyq
        self.highcut4 = self.highcut4 / nyq
        b4, a4 = signal.butter(8, [self.lowcut4, self.highcut4], 'bandpass')
        w4, h4 = signal.freqz(b4, a4)

        self.lowcut5 = self.lowcut5 / nyq
        b5, a5 = signal.butter(10, self.lowcut5, 'highpass')
        w5, h5 = signal.freqz(b5, a5)

        w1 = w1 * nyq / (np.pi)
        w2 = w2 * nyq / (np.pi)
        w3 = w3 * nyq / (np.pi)
        w4 = w4 * nyq / (np.pi)
        w5 = w5 * nyq / (np.pi)
        h1 = 20 * np.log10(abs(h1))
        h2 = 20 * np.log10(abs(h2))
        h3 = 20 * np.log10(abs(h3))
        h4 = 20 * np.log10(abs(h4))
        h5 = 20 * np.log10(abs(h5))

        plt.semilogx(w1, h1, w2, h2, w3, h3, w4, h4, w5, h5)
        axes = plt.gca()
        axes.set_ylim([-40, 10])
        plt.show()

        self.newSig = pygame.mixer.sound(
        self.filteredSig1 + self.filteredSig2 + self.filteredSig3 + self.filteredSig4 + self.filteredSig5)






















