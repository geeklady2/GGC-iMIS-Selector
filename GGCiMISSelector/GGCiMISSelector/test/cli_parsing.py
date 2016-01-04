__author__ = "Shannon Jaeger"

import unittest
import imisSelector
from test import capture
import os,sys

class ParserTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        # Reset Argv[0] to look like the main application is being run not the test suite
        sys.argv[0]= os.path.join(os.getcwd(), '..', 'imisSelector.py')
        cls.parser = imisSelector.parser()

    # def test_empty_args(self):
    #     """
    #     User passes no args, should fail with SystemExit
    #     """
    #     with self.assertRaises(SystemExit):
    #         self.parser.parse_args([])

    def test_help(self):
        """
        User has "-h" or "--help" parser fails with System Exit, but writes
        help information to the console
        :return:
        """
        cli_args = [os.path.join(os.getcwd(), '..', 'imisSelector.py')]

        cli_args.append('-h')
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue())

        cli_args[1] == '--help'
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue())

        cli_args[1] == '-help'
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue())

        # Even if there is a valid argument the help information should be shown when -h is given
        cli_args.append('-b')
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue())

    def test_version(self):
        """
        User has "-version" in the arguments the parser fails with System Exit,
        but writes the version information.
        :return:
        """

        cli_args = [os.path.join(os.getcwd(), '..', 'imisSelector.py')]
        cli_args.append('-version')
        with capture() as out:
            with self.assertRaises(SystemExit):
                parsed_args = self.parser.parse_args(cli_args)

            # The version info will appear in the std error text, check to see if it's correct
            self.assertEquals(out[1].getvalue(), 'imisSelector.py '+imisSelector.__version__+'\n')


        # Even if there is a valid argument the help information should be shown when -h is given
        cli_args.append('-b')
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertEquals(out[1].getvalue(), 'imisSelector.py '+imisSelector.__version__+'\n')




if __name__ == '__main__':
    unittest.main()
