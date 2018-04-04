import csv_stream_reader as r
import numpy as np


def test_key():

	subLineTest = 'key1:0.1;key2:2.\n'

	line = r.Line()
	subLine = r.SubLine()
	displayedKey = 'key2'

	line.str = subLineTest
	line.convertToDictionary()
	displayedValue = line.read_value(displayedKey)

	print ('value', displayedValue)
	assert displayedValue == 2.


def test_missing_key():

	subLineTest = 'key1:0.1;key:2.\n'

	line = r.Line()
	subLine = r.SubLine()
	displayedKey = 'key2'

	line.str = subLineTest
	line.convertToDictionary()
	displayedValue = line.read_value(displayedKey)

	print ('value', displayedValue)
	assert np.isnan(displayedValue)


def test_empty_line():

	subLineTest = ''

	line = r.Line()
	subLine = r.SubLine()
	displayedKey = 'key2'

	line.str = subLineTest
	line.convertToDictionary()
	displayedValue = line.read_value(displayedKey)

	print ('value', displayedValue)
	assert np.isnan(displayedValue)


def test_read_subline():

	subLineBytes = b'key1:0.1;key2:2.\n'

	subLine = r.SubLine()
	
	subLine.acquire(subLineBytes)

	assert isinstance(subLine.str, str) and subLine.str == 'key1:0.1;key2:2.'


def test_contenate_sublines():

	subLine1 = 'key1:0.1\n'
	subLine2 = ';key2:2.\n'

	line = r.Line()
	subLine = r.SubLine()

	subLine.str = subLine1
	line.concatenate(subLine)

	subLine.str = subLine2
	line.concatenate(subLine)

	assert line.str == 'key1:0.1\n;key2:2.\n'


def test_contenate_sublines2():

	subLine1 = b'key1:0.1\n'
	subLine2 = b';key2:2.\n'

	line = r.Line()
	subLine = r.SubLine()

	subLine.acquire(subLine1)
	line.concatenate(subLine)

	subLine.acquire(subLine2)
	line.concatenate(subLine)

	assert line.str == 'key1:0.1;key2:2.'


def test_acquire_whitespace():

	subLine1 = b'key1:0.1\n '

	subLine = r.SubLine()

	subLine.acquire(subLine1)

	assert subLine.str == 'key1:0.1'


def test_find_end():

	subLine1 = b'key1:0.1\n'

	subLine = r.SubLine()

	subLine.acquire(subLine1)

	assert not subLine.endFound


def test_find_end2():

	subLine1 = b'key1:0.1;end\n'

	subLine = r.SubLine()

	subLine.acquire(subLine1)

	assert subLine.endFound


def test_find_end3():

	subLine1 = b'key1:0.1;end\n'

	line = r.Line()
	subLine = r.SubLine()

	subLine.acquire(subLine1)
	line.concatenate(subLine)

	assert line.endFound


def test_count_packets():

	subLine1 = b'key1:0.1;end\n'

	line = r.Line()
	subLine = r.SubLine()

	subLine.acquire(subLine1)
	line.concatenate(subLine)

	assert line.nbPacketsMem == 1


def test_count_packets2():

	subLine1 = b'key1:0.1;end\n'
	subLine2 = b'key1:0.1;key2:2.;end\n'

	line = r.Line()
	subLine = r.SubLine()

	subLine.acquire(subLine1)
	line.concatenate(subLine)
	line.clear()

	subLine.acquire(subLine2)
	line.concatenate(subLine)

	assert line.nbPacketsMem ==  1 and line.nbPackets == 2
