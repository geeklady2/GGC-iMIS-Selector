__author__ = 'shannonjaeger'

class InvalidImisFile(Exception):
    """
    Raise when the contents of a file is not in the expected format, does
    not contain iMIS data.
    """
    pass

class NoImisFile(Exception):
    """
    Raise when no file path to an iMIS data file has been provided.
    """
    pass


