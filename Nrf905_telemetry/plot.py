import configparser
import time
import logging
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import parser_ as pars

logging.basicConfig(level=logging.INFO)

lineStyleArgs = {}
lineStyleArgs['solid'] = 'solid'
lineStyleArgs['dashed'] = QtCore.Qt.DashLine
lineStyleArgs['dotted'] = QtCore.Qt.DotLine

keys = ['key1', 'key2']  # , 'key3', 'key4']
legends = ['lgd1', 'lgd2', 'lgd3', 'lgd4']

Config = configparser.ConfigParser()
Config.read("telemetry.ini")
serialParams = pars.ConfigSectionMap("Serial", Config)
displayParams = pars.ConfigSectionMap("Display", Config)

Config.read("default.ini")
defaultPlotParams = pars.ConfigSectionMap("Plot", Config)

start = time.time()


class Data():

    def __init__(self, dummySignal, outputFile):
        self.dummySignal = dummySignal
        self.outputFile = outputFile

    # Realtime data plot. Each time this function is called, the data display is updated
    def updateData(self, displayedKey, displayedValue, ptr, ser, line, subLine):

        updated_line = False

        if not self.dummySignal:
            subLine.acquire(ser.readline())
            line.concatenate(subLine)
            if line.endFound:
                line.convertToDictionary()
                line.write(self.outputFile)
                displayedValue = line.read_value(displayedKey, displayedValue)
                line.clear()
                updated_line = True
            subLine.clear()
        else:
            displayedValue = []
            for i in range(len(displayedKey)):
                displayedValue.append(np.cos(0.05 * ptr) + i)

        # logging.debug('\n'+'Displayed values')
        # for key in displayedValue:
        #     message = ':'.join([str(key)])
        #     logging.debug(message)

        return updated_line, displayedValue

    def updateFromFile(self, displayedKey, displayedValue, line_from_file, line, subLine):

        updated_line = False

        line.str = line_from_file
        line.find_end()
        if line.endFound:
            line.convertToDictionary()
            displayedValue = line.read_value(displayedKey, displayedValue)
            line.clear()
            updated_line = True
        subLine.clear()

        return updated_line, displayedValue


class Plot():

    def __init__(self, ):
        self.win = pg.GraphicsWindow(
            title="Signal from serial port")  # creates a window
        self.win.resize(1420, 840)
        self.lineStyle = []
        self.colors = []
        self.curves = []
        self.ptr = 0.
        self.timeChunkSize = 40
        self.start = time.time()

    def setLines(self, defaultPlotParams):
        assert (defaultPlotParams['maxlineperplot'] <=
                len(defaultPlotParams['linestyle']))
        for s in defaultPlotParams['linestyle']:
            self.lineStyle.append(lineStyleArgs[s])

    def setColors(self, defaultPlotParams):
        assert (defaultPlotParams['maxlineperplot'] <=
                len(defaultPlotParams['linecolor']))
        for c in defaultPlotParams['linecolor']:
            self.colors.append(c)

    def setCurves(self, displayParams):
        for i, k in enumerate(keys):
            plt = self.win.addPlot(title="Realtime plot")
            plt.addLegend()
            plt.showGrid(x=True, y=True, alpha=0.5)
            self.curves.append([])
            for j, p in enumerate(displayParams[k]):
                # create an empty "plot" (a curve to plot)
                self.curves[i].append(
                    plt.plot(name=displayParams[legends[i]][j], size=18))
            # CHANGE THE FONT SIZE AND COLOR OF ALL LEGENDS LABEL
            legendLabelStyle = {'color': '#FFF',
                                'size': '12pt', 'bold': True, 'italic': False}
            for item in plt.legend.items:
                for single_item in item:
                    if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                        single_item.setText(
                            single_item.text, **legendLabelStyle)

    def checkParams(self, displayParams, defaultPlotParams):
        assert (len(displayParams['key1']) <=
                defaultPlotParams['maxlineperplot'])

    def updatePlot(self, Xms, displayedValue):

        # shift data in the temporal mean 1 sample left
        for xm in Xms:
            xm[:-1] = xm[1:]

        # vector containing the instantaneous values
        self.ptr += 1  # update x position for displaying the curve
        index = 0
        for p in self.curves:
            for i, c in enumerate(p):
                c.setPos(self.ptr, 0)
                Xms[index][-1] = float(displayedValue[index])
                if self.lineStyle[i] == 'solid':
                    c.setData(Xms[index] + 1e-16,
                              pen=pg.mkPen(self.colors[i], width=5))
                else:
                    c.setData(Xms[index] + 1e-16, pen=pg.mkPen(
                        self.colors[i], width=5, style=self.lineStyle[i]))
                # set x position in the graph to 0
                index += 1

        QtGui.QApplication.processEvents()  # you MUST process the plot now

        return Xms, displayedValue

    def run(self, Xms, displayedKey, displayedValue, data, ser, line, subLine):

        incr = 1
        while True:
            Xms, displayedValue = self.updatePlot(Xms, displayedValue)
            updatedLine, displayedValue = data.updateData(
                displayedKey, displayedValue, self.ptr, ser, line, subLine)
            if updatedLine:
                incr += 1
                if incr % self.timeChunkSize == 0:
                    logging.info(
                        'Reading frequency = %.3f packets per second', incr / (time.time() - self.start))
                    incr = 0
                    self.start = time.time()
