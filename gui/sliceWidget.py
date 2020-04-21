import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.patches as patches
from PyQt5.Qt import *


class SliceWidget(FigureCanvas):
    def __init__(self, parent=None, dpi=100):
        # Create figure and axes, the axes should cover the entire figure size
        figure = Figure(dpi=dpi, frameon=False)
        self.axes = figure.add_axes((0, 0, 1, 1), facecolor='black')

        # Hide the x and y axis, we just want to see the image
        self.axes.get_xaxis().set_visible(True)
        self.axes.get_yaxis().set_visible(True)

        # Initialize the parent FigureCanvas
        FigureCanvas.__init__(self, figure)
        self.setParent(parent)

        # Set background of the widget to be close to black
        # The color is not made actually black so that the user can distinguish the image bounds from the figure bounds
        self.setStyleSheet('background-color: #FFFFFF;')

        # Set widget to have strong focus to receive key press events
        self.setFocusPolicy(Qt.StrongFocus)

        # Create navigation toolbar and hide it
        # We don't want the user to see the toolbar but we are making our own in the user interface that will call
        # functions from the toolbar
        self.toolbar = NavigationToolbar(self, self)
        self.toolbar.hide()

        # Update size policy and geometry
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def updateFigure(self):
        # Clear the axes
        self.axes.cla()

        # Draw the figure now
        self.draw()

