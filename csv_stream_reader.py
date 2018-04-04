import numpy as np


class Line():
	def __init__(self,):
		self.str = ''
		self.dict = {}
		self.nbPackets = 0
		self.nbPacketsMem = 0
		self.endFound = False

	def concatenate(self, subLine):
		self.str += subLine.str
		self.nbPackets += subLine.nbPackets
		if subLine.endFound:
			self.nbPacketsMem = self.nbPackets
			self.endFound = True
			try:
				self.detect_incoherent_nb_packets()	
			except ValueError as err:
				print(err.args)

	def clear(self,):
		self.str = ''
		self.dict = {}
		self.nbPackets = 0
		self.endFound = False

	def convertToDictionary(self,):

		packets = self.str.split(';')
		for p in packets:
			if len(p.split(':')) > 1:
				key = p.split(':')[0]
				value = p.split(':')[1]
				self.dict[key] = value

	def read_value(self, key):
		try:
			displayedValue = float(self.dict[key])
		except:
			displayedValue = np.nan
			print('%s not successfully read' % key)
		return displayedValue

	def detect_incoherent_nb_packets(self):
		if self.nbPacketsMem > 0 and self.nbPacketsMem != self.nbPackets:
			raise ValueError('WARNING, the expected number of packets is',\
			 self.nbPacketsMem, 'while the actual number is', self.nbPackets)


class SubLine():
	def __init__(self,):
		self.str = ''
		self.endFound = False
		self.nbPackets = 0

	def acquire(self, line):
		l = line.rstrip()
		l = l.rstrip(b'\n')
		try:
			self.str = l.decode("utf-8")
			# print (self.str)
		except:
			print('Line from serial port could not be converted to unicode')
			self.str = ''
		self.find_end()

	def clear(self,):
		self.str = ''
		self.endFound = False
		self.nbPackets = 0

	def find_end(self,):
		packets = self.str.split(';')
		count = 0
		for p in packets:
			count += 1
			if p.rstrip() == 'end':
				self.endFound = True
			self.nbPackets = count - 1
