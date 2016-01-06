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

    def test_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args([])
            self.assertIn('usage:', out[1].getvalue(), 'empty arguments not detected')

    def test_bad_args(self):
        """
            Test a variety of incorrect sets of arguments
        """

        # Select command with a bad argument
        cli_args = ['select', '-x']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'bad -x option not dectected.')

        # merge command with a bad argument
        cli_args = ['merge', '-m', '/somedir/somefile.txt', '-c', '/somedir/someotherfile.txt', '-v2']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'bad -v2 option with merge command not dectected.')

        # select command with two -i args
        cli_args = ['merge', '-i', 'somefile.csv', '-i', 'someotherfile.csv', '-v2']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'bad -v2 option with merge command not dectected.')

        # bad command
        cli_args = ['badcommand', '-m', 'somefile.txt', '-c', '/somedir/someotherfile.txt', '-xyz']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'command "badcommand" not detected.')

        # bad optional option
        cli_args = ['select', '-b', '-r']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), '"select" command missing -i option not detected.')

        # Test invalid verbosity level
        cli_args = ['select', '-i', 'myfile.csv', '-n', '3', '-vb', '4']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'Failed to dectect invalid verbosity mode.')


    def test_help(self):
        """
        User has "-h" or "--help" parser fails with System Exit, but writes
        help information to the console
        """

        # Try the various flavours of -h
        cli_args = ['-h']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue(), 'Help not displayed with -h option.')

        cli_args = ['--help']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue(), 'Help not displayed for --help option.')

        cli_args = ['-help']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue(), 'Help not displayed for -help option.')

        # Get help for the "select" command
        cli_args = ['select', 'help']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue())
            self.assertIn('-i IMIS_FILE', out[1].getvalue(), 'Help for "select" command not displayed.')
            self.assertIn('-n NUM', out[1].getvalue(), 'Help for ""select command not displayed.')


               # Get help for the "select" command
        cli_args = ['merge', 'help']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[1].getvalue())
            self.assertIn('-i IMIS_FILE', out[1].getvalue(), 'Help for "merge" command not displayed.')
            self.assertIn('-m MEMBER_FILE', out[1].getvalue(), 'Help for "merge" command not displayed.')


        # Even if there is a valid argument the help information should be shown when -h is given
        cli_args = ['select', '-i', 'somefile.csv', '-b', '-h']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertIn('usage:', out[0].getvalue(), 'Help not displayed when other valid args are give.')

    def test_version(self):
        """
        User has "-version" in the arguments the parser fails with System Exit,
        but writes the version information.
        :return:
        """

        cli_args = ['--version']
        with capture() as out:
            with self.assertRaises(SystemExit):
                parsed_args = self.parser.parse_args(cli_args)

            # The version info will appear in the std error text, check to see if it's correct
            self.assertEquals(out[1].getvalue(), 'imisSelector.py '+imisSelector.__version__+'\n',
                              '"--version" incorrect, "{0}" displayed'.format(out[1].getvalue()))

        cli_args = ['-v']
        with capture() as out:
            with self.assertRaises(SystemExit):
                parsed_args = self.parser.parse_args(cli_args)
            self.assertEquals(out[1].getvalue(), 'imisSelector.py '+imisSelector.__version__+'\n',
                              '"-v" incorrect, "{0}" displayed'.format(out[1].getvalue()))

        # Version isn't allowed with other arguments
        cli_args = ['select', '-b', '-i', 'myfile.csv', '-v']
        with capture() as out:
            with self.assertRaises(SystemExit):
                self.parser.parse_args(cli_args)
            self.assertEquals(out[1].getvalue(), 'imisSelector.py select '+imisSelector.__version__+'\n',
                            '"-v" with other options incorrect, "{0}" displayed'.format(out[1].getvalue()))

    def test_verbosity(self):
        """
        Test valid and invalid verbosity options
        """

        # Test quiet, verbosity of 0, level
        try:
            cli_args = ['select', '-i', 'myfile.csv', '-n', '3']
            results = self.parser.parse_args(cli_args)
            self.assertEquals(results.verbose, 0)
        except Exception as e:
            self.fail('Unexpected Exception: ' + str(e))

        # Test nearly quiet, verbosity 1
        try:
            cli_args = ['select', '-i', 'myfile.csv', '-n', '3', '-vb', '1']
            results = self.parser.parse_args(cli_args)
            self.assertEquals(results.verbose[0], 1)
        except Exception as e:
            self.fail('Unexpected Exception: ' + str(e))

        # Test moderate noise verbosity 2
        try:
            cli_args = ['select', '-i', 'myfile.csv', '-n', '3', '-vb', '2']
            results = self.parser.parse_args(cli_args)
            self.assertEquals(results.verbose[0], 2)
        except Exception as e:
            self.fail('Unexpected Exception: ' + str(e))

        # Test loud verbosity 3
        try:
            cli_args = ['select', '-i', 'myfile.csv', '-n', '3', '-vb', '3']
            results = self.parser.parse_args(cli_args)
            self.assertEquals(results.verbose[0], 3)
        except Exception as e:
            self.fail('Unexpected Exception: ' + str(e))



if __name__ == '__main__':
    unittest.main()
