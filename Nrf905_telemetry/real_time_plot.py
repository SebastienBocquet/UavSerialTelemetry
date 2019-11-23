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
    read_from_file = serialParams['read_from_file']
    display_every = serialParams['display_every']

    # Create object serial port
    try:
        ser = serial.Serial(serialParams['port_name'], serialParams['baud_rate'])
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

    line = reader.Line()
    subLine = reader.SubLine()

    if read_from_file:
        log_filename = input('Enter log filename to be read : ')
        data = plt.Data(dummySignal, None)
    else:
        log_filename = input('Enter log filename to be written : ')
        if log_filename == '':
            log_filename = 'default_telemetry.out'
        file = open(log_filename, 'wb')
        data = plt.Data(dummySignal, file)

    displayedValue = np.empty((len(displayedKey)))

    # width of the window displaying the curve
    window_width = displayParams['window_width']

    # create array that will contain the relevant time series
    xms = []
    for i in range(len(displayedKey)):
        xms.append(np.linspace(0, 0, window_width))

    plot = plt.Plot()
    plot.checkParams(displayParams, defaultPlotParams)
    plot.setCurves(displayParams)
    plot.setColors(defaultPlotParams)
    plot.setLines(defaultPlotParams)
    plot.ptr = -window_width

    if read_from_file:
        file = open(log_filename)
        for l in file.readlines():
            xms, displayedValue = plot.updatePlot(xms, displayedValue)
            updated_line, displayedValue = data.updateFromFile(displayedKey, displayedValue, l, line, subLine)
        file.close()
    else:
        plot.run(xms, displayedKey, displayedValue, data, ser, line, subLine, display_every)
        file.close()

    pg.QtGui.QApplication.exec_()  # you MUST put this at the end
