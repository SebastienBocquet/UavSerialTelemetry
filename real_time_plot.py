import sys
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg
import serial
import configparser
import json
import parser_ as pars
import csv_stream_reader as reader


Config = configparser.ConfigParser()
Config.read("telemetry.ini")
serialParams = pars.ConfigSectionMap("Serial", Config)
displayParams = pars.ConfigSectionMap("Display", Config)


# Create object serial port
ser = serial.Serial(serialParams['portname'], serialParams['baudrate'])

### START QtApp #####
# you MUST do this once (initialize things)
app = QtGui.QApplication([])
####################

win = pg.GraphicsWindow(title="Signal from serial port")  # creates a window
# creates empty space for the plot in the window
p = win.addPlot(title="Realtime plot")
curve = p.plot()                        # create an empty "plot" (a curve to plot)

# width of the window displaying the curve
windowWidth = displayParams['windowwidth']
# create array that will contain the relevant time series
Xm = np.linspace(0, 0, windowWidth)
ptr = -windowWidth                      # set first x position

displayedKey = displayParams['key']

line = reader.Line()
subLine = reader.SubLine()
displayedValue = np.nan


# Realtime data plot. Each time this function is called, the data display is updated
def update():

    global curve, ptr, Xm, displayedValue
    # shift data in the temporal mean 1 sample left
    Xm[:-1] = Xm[1:]

    subLine.acquire(ser.readline())
    line.concatenate(subLine)
    if line.endFound:
    	line.convertToDictionary()
    	displayedValue = line.read_value(displayedKey)
    	line.clear()
    subLine.clear()

    # vector containing the instantaneous values
    Xm[-1] = float(displayedValue)
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr, 0)                   # set x position in the graph to 0
    QtGui.QApplication.processEvents()    # you MUST process the plot now


if __name__ == '__main__':

    while True:
        update()
        # delay(1000)

    pg.QtGui.QApplication.exec_()  # you MUST put this at the end
