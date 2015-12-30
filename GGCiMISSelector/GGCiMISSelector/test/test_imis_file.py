__author__ = "Shannon Jaeger"

import unittest
from ImisFile import ImisFile
from Exceptions import *
import os

class TestImisFiles(unittest.TestCase):


    def test_read(self):
        try:
            imis_file = ImisFile()
            imis_file.read()
            self.fail('No error was reported when reading before file path was set.')
        except NoImisFile:
            pass
        else:
            self.fail('Unexpected Exception has occured.')

    def setget_path_test(self):
        imis_file = ImisFile()

        imis_file.set_file_path(None)
        self.assertIsNone(imis_file.get_file_path(), 'Failed to set the file path to None.')

        imis_file.set_file_path('')
        self.assertEqual(imis_file.get_file_path(), '', 'Failed to set the file path to the empty string.')

        imis_file.set_file_path('Black')
        self.assertEqual(imis_file.get_file_path(), 'Black', 'Failed to set the file path to "Black".')

        imis_file.set_file_path('/tmp/afile.csv')
        self.assertEqual(imis_file.get_file_path(), 'Black', 'Failed to set the file path to "/tmp/afile.csv".')

    def no_file_test(self):
        try:
            file_path = os.path.join( os.getcwd(), 'data', 'nosuchfile.csv')
            imis_file = ImisFile(file_path)
            self.fail('Exception "FileNotFoundError" was not thrown')
        except os.FileNotFoundError:
            pass
        except:
            self.fail('Unexpected exception thrown.')


    def empty_file_test(self):
        try:
            file_path = os.path.join( os.getcwd(), 'data', 'empty_file.csv')
            imis_file = ImisFile(file_path)
            self.fail('Exception "InvalidImisFile" was not thrown.')
        except InvalidImisFile:
            pass
        except:
            self.fail('Unexpected exception thrown.')


    def no_heading_test(self):
        try:
            file_path = os.path.join( os.getcwd(), 'data', 'noheadings.csv')
            imis_file = ImisFile(file_path)
            self.fail('Exception "InvalidImisFile" was not thrown.')
        except InvalidImisFile:
            pass
        except:
            self.fail('Unexpected exception thrown.')


    def non_csvfils_test(self):
        try:
            file_path = os.path.join( os.getcwd(), 'data', 'data.txt')
            imis_file = ImisFile(file_path)
            self.fail('Exception "InvalidImisFile" was not thrown.')
        except InvalidImisFile:
            pass
        except Exception as e:
            print(e.message)
            self.fail('Unexpected exception thrown.')



if __name__ == '__main__':
    unittest.main()
