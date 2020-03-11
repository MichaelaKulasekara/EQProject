import os
import logging
import numpy as np

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


    @pyqtSlot(int)
    def on_sliceSlider_valueChanged(self, value):
        print('slice number: %d' % value)
        self.sliceWidgetBMode.sliceNumber = value
        self.sliceWidgetIQ.sliceNumber = value
        self.labelSlice.setText('Slice: %d' % value)
        self.sliceWidgetBMode.updateFigure(self.roiDataList, self.landMarkViewNumber, self.ptSettings)
        self.sliceWidgetIQ.updateFigure(self.roiDataList, self.landMarkViewNumber, self.ptSettings)
