import configparser
import logging

import csv_stream_reader as reader
import numpy as np
import parser_ as pars
import plot as plt
import pyqtgraph as pg
import serial
from pyqtgraph.Qt import QtGui

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    Config = configparser.ConfigParser()
    Config.read("telemetry.ini")
    serialParams = pars.ConfigSectionMap("Serial", Config)
    displayParams = pars.ConfigSectionMap("Display", Config)

    Config.read("default.ini")
    defaultPlotParams = pars.ConfigSectionMap("Plot", Config)

    logging.info('\n' + 'Displayed variables')
    for key, value in displayParams.items():
        message = ':'.join([str(key), str(value)])
        logging.info(message)

    logging.info('\n' + 'Parameters used for plotting')
    for key, value in defaultPlotParams.items():
        message = ':'.join([str(key), str(value)])
        logging.info(message)

    dummySignal = False

    # Create object serial port
    try:
        ser = serial.Serial(serialParams['portname'], serialParams['baudrate'])
    except:
        ser = None
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
    # for k in displayParams['key3']:
    #    displayedKey.append(k)
    # for k in displayParams['key4']:
    #    displayedKey.append(k)

    line = reader.Line()
    subLine = reader.SubLine()

    data = plt.Data(dummySignal)

    displayedValue = np.empty((len(displayedKey)))

    # width of the window displaying the curve
    windowWidth = displayParams['windowwidth']

    # create array that will contain the relevant time series
    xms = []
    for i in range(len(displayedKey)):
        xms.append(np.linspace(0, 0, windowWidth))

    plot = plt.Plot()
    plot.checkParams(displayParams, defaultPlotParams)
    plot.setCurves(displayParams)
    plot.setColors(defaultPlotParams)
    plot.setLines(defaultPlotParams)
    windowWidth = displayParams['windowwidth']
    plot.ptr = -windowWidth
    plot.run(xms, displayedKey, displayedValue, data, ser, line, subLine)

    pg.QtGui.QApplication.exec_()  # you MUST put this at the end
