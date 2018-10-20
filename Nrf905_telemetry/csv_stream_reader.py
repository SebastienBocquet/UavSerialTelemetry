import numpy as np
import logging

logging.basicConfig(level=logging.INFO)


class Line():
    def __init__(self, ):
        self.str = ''
        self.dict = {}
        self.nbPackets = 0
        self.nbPacketsMem = 0
        self.endFound = False

    def concatenate(self, subLine):
        self.str += subLine.str
        self.nbPackets += subLine.nbPackets
        self.find_end()
        if self.endFound:
            self.nbPacketsMem = self.nbPackets
            self.endFound = True
            logging.debug('Number of read telemetry quantities %d' % self.nbPackets)
            try:
                self.detect_incoherent_nb_packets()
            except ValueError as err:
                logging.debug(err.args)

    def clear(self, ):
        self.str = ''
        self.dict = {}
        self.nbPackets = 0
        self.endFound = False

    def convertToDictionary(self, ):
        packets = self.str.split(';')
        for p in packets:
            key = p[:2]
            value = p[2:]
            self.dict[key] = value

        logging.debug('read data arranged in following dictionnary')
        for key, value in self.dict.items():
            message = ':'.join([str(key), str(value)])
            logging.debug(message)

    def read_value(self, key, displayedValue):
        for i, k in enumerate(key):
            try:
                displayedValue[i] = float(self.dict[k])
            except:
                displayedValue[i] = np.nan
                logging.info('%s not successfully read' % k)
        return displayedValue

    def detect_incoherent_nb_packets(self):
        if self.nbPacketsMem > 0 and self.nbPacketsMem != self.nbPackets:
            raise ValueError('WARNING, the expected number of packets is',
                             self.nbPacketsMem, 'while the actual number is', self.nbPackets)

    def find_end(self, ):
        packets = self.str.split(';')
        count = 0
        for p in packets:
            count += 1
            if p.rstrip() == 'end':
                self.endFound = True
            self.nbPackets = count - 1


class SubLine():
    def __init__(self, ):
        self.str = ''
        self.endFound = False
        self.nbPackets = 0

    def acquire(self, line):
        l = line.rstrip()
        l = l.rstrip(b'\n')
        try:
            self.str = l.decode("utf-8")
            logging.debug(self.str)
        except:
            logging.debug('Line from serial port could not be converted to unicode')
            self.str = ''
        self.find_end()

    def clear(self, ):
        self.str = ''
        self.endFound = False
        self.nbPackets = 0

    def find_end(self, ):
        packets = self.str.split(';')
        count = 0
        for p in packets:
            count += 1
            if p.rstrip() == 'end':
                self.endFound = True
            self.nbPackets = count - 1
