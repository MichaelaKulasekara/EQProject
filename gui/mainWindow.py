import os
import logging
import numpy as np
import audiofile as af
import ffmpeg

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


    @pyqtSlot(int)
    def on_gainSlider_band1_valueChanged(self, value):
        print('Band 1 Gain: %d' % value + '%')
        self.gainLabel1.setText('Band 1 Gain: %d' % value + '%')


    @pyqtSlot(int)
    def on_gainSlider_band2_valueChanged(self, value):
        print('Band 2 Gain: %d' % value + '%')
        self.gainLabel2.setText('Band 2 Gain: %d' % value + '%')

    @pyqtSlot(int)
    def on_gainSlider_band3_valueChanged(self, value):
        print('Band 3 Gain: %d' % value + '%')
        self.gainLabel3.setText('Band 3 Gain: %d' % value + '%')

    @pyqtSlot(int)
    def on_gainSlider_band4_valueChanged(self, value):
        print('Band 4 Gain: %d' % value + '%')
        self.gainLabel4.setText('Band 4 Gain: %d' % value + '%')

    @pyqtSlot(int)
    def on_gainSlider_band5_valueChanged(self, value):
        print('Band 5 Gain: %d' % value + '%')
        self.gainLabel5.setText('Band 5 Gain: %d' % value + '%')

    @pyqtSlot()
    def on_uploadAudio_clicked(self):
        fullPath, filterReturn = FileDialog.getOpenFileName(self, 'Select .wav file', self.defaultOpenPath, '*.wav')
        print(fullPath)
        self.filenameData = util.splitext((os.path.basename(fullPath)))
        filename = self.filenameData[0] + self.filenameData[1]
        print('Audio File Grabbed: ' + filename)
        sig, fs = af.read(filename)
        print('Original Sampling Rate: ' + str(fs) + ' Hz')








