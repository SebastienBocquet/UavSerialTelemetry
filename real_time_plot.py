import sys
sys.path.append("../flight_analyzer")
import telemetry_lib as lib
import toolbox as tool
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import serial
import copy
import configparser
import json


Config = configparser.ConfigParser()
lineDict = {}
line = ''
canReadLine = False


# # # lets create that config file for next time...
# cfgfile = open("telemetry.ini",'w')

# # add the settings to the structure of the file, and lets write it out...
# Config.add_section("Serial")
# Config.set("Serial","portName","COM4")
# Config.set('Serial','baudRate', '19200')
# Config.add_section("Display")
# Config.set("Display","key","sonh")
# Config.write(cfgfile)
# cfgfile.close()


def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = json.loads(Config.get(section, option))
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
    return dict1


def read_telemetry_line():
	global line, lineDict, canReadLine

	# TODO: Sometimes .decode() fails
	line += ser.readline().rstrip().decode("utf-8")
	packets = line.split(';')
	for p in packets:
		if p.rstrip() == 'end':
			# print ('found end of line')
			# print (line)
			canReadLine = True


def read_value(displayedKey):
	global line, lineDict, displayedValue, canReadLine
	if canReadLine:
		packets = line.split(';')
		for p in packets:
			if len(p.split(':')) > 1:
		 		key = p.split(':')[0]
		 		value = p.split(':')[1]
		 		lineDict[key] = value
		# print (lineDict)
		try:
			displayedValue = float(lineDict[displayedKey])
		except:
			print ('%s not successfully read' %displayedKey)
		lineDict = {}
		line = ''
		canReadLine = False




Config.read("telemetry.ini")
serialParams = ConfigSectionMap("Serial")
displayParams = ConfigSectionMap("Display")


# Create object serial port
ser = serial.Serial(serialParams['portname'], serialParams['baudrate'])

### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################

win = pg.GraphicsWindow(title="Signal from serial port") # creates a window
p = win.addPlot(title="Realtime plot")  # creates empty space for the plot in the window
curve = p.plot()                        # create an empty "plot" (a curve to plot)

windowWidth = displayParams['windowwidth']                       # width of the window displaying the curve
Xm = np.linspace(0,0,windowWidth)          # create array that will contain the relevant time series     
ptr = -windowWidth                      # set first x position

displayedValue = np.nan
displayedKey = displayParams['key']




# Realtime data plot. Each time this function is called, the data display is updated
def update():

	global curve, ptr, Xm, line, lineDict, displayedValue, canReadLine
	Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left

	read_telemetry_line()
	read_value(displayedKey)

	Xm[-1] = float(displayedValue)                 # vector containing the instantaneous values      
	ptr += 1                              # update x position for displaying the curve
	curve.setData(Xm)                     # set the curve with this data
	curve.setPos(ptr,0)                   # set x position in the graph to 0
	QtGui.QApplication.processEvents()    # you MUST process the plot now



if __name__ == '__main__':

	while True:
		update()
		# delay(1000)

	pg.QtGui.QApplication.exec_() # you MUST put this at the end