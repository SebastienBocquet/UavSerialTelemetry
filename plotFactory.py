import configparser
import parser_ as pars
import pyqtgraph as pg
import sys
from pyqtgraph.Qt import QtCore


lineStyleArgs = {}
lineStyleArgs['solid'] = 'solid'
lineStyleArgs['dashed'] = QtCore.Qt.DashLine
lineStyleArgs['dotted'] = QtCore.Qt.DotLine

keys = ['key1', 'key2'] #, 'key3', 'key4']
legends = ['lgd1', 'lgd2', 'lgd3', 'lgd4']

Config = configparser.ConfigParser()
Config.read("telemetry.ini")
serialParams = pars.ConfigSectionMap("Serial", Config)
displayParams = pars.ConfigSectionMap("Display", Config)

Config.read("default.ini")
defaultPlotParams = pars.ConfigSectionMap("Plot", Config)

print(displayParams)
print(defaultPlotParams)


class plot():

	def __init__(self,):
		self.win = pg.GraphicsWindow(title="Signal from serial port")  # creates a window
		self.win.resize(1420, 840)
		self.lineStyle = []
		self.colors = []
		self.curves = []

	def setLines(self, defaultPlotParams):
		for s in defaultPlotParams['linestyle']:
			self.lineStyle.append(lineStyleArgs[s])

	def setColors(self, defaultPlotParams):
		for c in defaultPlotParams['linecolor']:
			self.colors.append(c)

	def setCurves(self, displayParams):
		for i,k in enumerate(keys):
			plt = self.win.addPlot(title="Realtime plot")
			plt.addLegend()
			plt.showGrid(x=True,y=True,alpha=0.5)
			self.curves.append([])
			for j,p in enumerate(displayParams[k]):
				# create an empty "plot" (a curve to plot)
				self.curves[i].append(plt.plot(name=displayParams[legends[i]][j], size = 18))
			# CHANGE THE FONT SIZE AND COLOR OF ALL LEGENDS LABEL
			legendLabelStyle = {'color': '#FFF', 'size': '12pt', 'bold': True, 'italic': False}
			for item in plt.legend.items:
				for single_item in item:
					if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
						single_item.setText(single_item.text, **legendLabelStyle)

	def checkParams(self, displayParams, defaultPlotParams):
		assert(len(displayParams['key1']) <= defaultPlotParams['maxlineperplot'])


plot = plot()
plot.checkParams(displayParams, defaultPlotParams)
plot.setCurves(displayParams)
plot.setColors(defaultPlotParams)
plot.setLines(defaultPlotParams)