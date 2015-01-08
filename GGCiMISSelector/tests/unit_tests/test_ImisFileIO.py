from unittest import TestCase
from GGCiMISSelector import exceptions
from GGCiMISSelector import imisFileIO

__author__ = 'Shannon Jaeger'
__project__ = 'Test IMIS Selector'

from GGCiMISSelector.imisFileIO import ImisFileIO
from GGCiMISSelector.exceptions import GGCFileDoesNotExist
from GGCiMISSelector.exceptions import GGCInvalidImisFile

import os

class TestImisFileIO(TestCase):
    def testNoFile(self):
        try:
            iMIS_file = ImisFileIO(os.curdir+'/tests/data/nosuchfile.csv')
            fail()
        except GGCFileDoesNotExist:
            self.assertRaises(GGCFileDoesNotExist)

    def testEmptyFile(self):
        try:
            print( 'opening file ' + os.getcwd()+'../data/empty.csv')
            iMIS_file = ImisFileIO(os.getcwd()+'/../data/empty.csv')
            data = iMIS_file.read()
            fail()
        except GGCInvalidImisFile:
            self.assertRaises(GGCInvalidImisFile)

    def testNoColumnHeadings(self):
        try:
            iMIS_file = ImisFileIO(os.getcwd()+'/../data/noheadings.csv')
            data = iMIS_file.read()
            fail()
        except GGCInvalidImisFile:
            self.assertRaises(GGCInvalidImisFile)

    def testNoData(self):
        try:
            iMIS_file = ImisFileIO(os.getcwd()+'/../data/nodata.csv')
            data = iMIS_file.read()
            fail()
        except GGCInvalidImisFile:
            self.assertRaises(GGCInvalidImisFile)


if __name__ == '__main__':
    unittest.main()