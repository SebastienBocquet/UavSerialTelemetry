import sys
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import serial
import configparser
import json
import parser_ as pars
import csv_stream_reader as reader
import time
import plotFactory as pltF
import logging

logging.basicConfig(level=logging.INFO)


Config = configparser.ConfigParser()
Config.read("telemetry.ini")
serialParams = pars.ConfigSectionMap("Serial", Config)
displayParams = pars.ConfigSectionMap("Display", Config)

Config.read("default.ini")
defaultPlotParams = pars.ConfigSectionMap("Plot", Config)

logging.info('\n'+'Displayed variables')
for key, value in displayParams.items():
    message = ':'.join([str(key), str(value)])
    logging.info(message)

logging.info('\n'+'Parameters used for plotting')
for key, value in defaultPlotParams.items():
    message = ':'.join([str(key), str(value)])
    logging.info(message)

dummySignal = False

# Create object serial port
try:
    ser = serial.Serial(serialParams['portname'], serialParams['baudrate'])
except:
    logging.info('No data on serial port: generating a dummy signal for testing')
    dummySignal = True

### START QtApp #####
# you MUST do this once (initialize things)
app = QtGui.QApplication([])
####################

displayedKey = []
for k in displayParams['key1']:
    displayedKey.append(k)
for k in displayParams['key2']:
    displayedKey.append(k)
#for k in displayParams['key3']:
#    displayedKey.append(k)
#for k in displayParams['key4']:
#    displayedKey.append(k)

line = reader.Line()
subLine = reader.SubLine()
displayedValue = np.empty((len(displayedKey)))


# Realtime data plot. Each time this function is called, the data display is updated
def updateData():

    global displayedValue

    updated_line = False

    if not dummySignal:
        subLine.acquire(ser.readline())
        line.concatenate(subLine)
        if line.endFound:
            line.convertToDictionary()
            displayedValue = line.read_value(displayedKey, displayedValue)
            line.clear()
            updated_line = True
        subLine.clear()
    else:
        displayedValue = []
        for i, k in enumerate(displayedKey):
            displayedValue.append(np.cos(0.05 * ptr) + i)

    logging.debug('\n'+'Displayed values')
    for key in displayedValue:
        message = ':'.join([str(key)])
        logging.debug(message)

    return updated_line


def updatePlot():

    global ptr, Xm, displayedValue

    # shift data in the temporal mean 1 sample left
    for xm in Xms:
        xm[:-1] = xm[1:]

    # vector containing the instantaneous values
    ptr += 1 # update x position for displaying the curve
    index = 0
    for p in plot.curves:
        for i, c in enumerate(p):
            c.setPos(ptr, 0)
            Xms[index][-1] = float(displayedValue[index])
            if plot.lineStyle[i] == 'solid':
                c.setData(Xms[index]+1e-16, pen=pg.mkPen(plot.colors[i], width=5))
            else:
                c.setData(Xms[index]+1e-16, pen=pg.mkPen(
                    plot.colors[i], width=5, style=plot.lineStyle[i]))
            # set x position in the graph to 0
            index += 1

    QtGui.QApplication.processEvents()    # you MUST process the plot now


if __name__ == '__main__':

    start = time.time()
    TimeChunkSize = 40

    # width of the window displaying the curve
    windowWidth = displayParams['windowwidth']
    # create array that will contain the relevant time series
    Xms = []
    for i in range(len(displayedKey)):
        Xms.append(np.linspace(0, 0, windowWidth))
    ptr = -windowWidth                      # set first x position

    plot = pltF.plot

    incr = 1
    while True:
        updatePlot()
        updatedLine = updateData()
        if updatedLine:
            incr += 1
            if incr % TimeChunkSize == 0:
                logging.info('Reading frequency = %.3f packets per second', incr / (time.time() - start))
                incr = 0
                start = time.time()

    pg.QtGui.QApplication.exec_()  # you MUST put this at the end
