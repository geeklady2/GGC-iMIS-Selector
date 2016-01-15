__title__ = 'names'
__version__ = '0.0.1'
__licence__ = '????'

# Losely based on code developed by Trey Hunner at https://github.com/treyhunner/names

import os
from random import random
from bisect import bisect

class SingletonMetaClass(type):
    def __init__(cls, name, bases, dict):
        super(SingletonMetaClass, cls).__init__(name, bases, dict)
        original_new = cls.__new__

        def my_new(cls, *args, **kwds):
            if cls.instance == None:
                cls.instance = original_new(cls, *args, **kwds)
                return cls.instance
        cls.instance = None
        cls.__new__ = staticmethod(my_new)

class NameGenerator(object):
    __module__ = SingletonMetaClass

    def __init__(self, data_dir=None):
        """
        Read data from the
        :param data_dir: The directory containing the data files
        :return:
        """

        self._last_file_name   = 'dist.all.last'
        self._female_file_name = 'dist.female.first'
        self._male_file_name   = 'dist.male.first'

        self._female_names = []
        self._male_names   = []
        self._last_names   = []

        self.data_dir = None
        if data_dir is not None:
            self.set_data_dir(data_dir)

    def set_data_dir(self, data_dir=None):
        """
        Set the directory/folder that the data files reside in.
        :param data_dir:  The directory
        """

        if data_dir is None:
            self.data_dir = os.getcwd()
        else:
            self.data_dir = data_dir


    def get_data_dir(self):
        """
        Get the full path to the directory containing the data files.
        :return os.path: path to the data files or None if it is not set
        """
        return self.data_dir

    def load_data(self):
        """
        If creating a number of random names it will be more time efficient then re-reading the
        data files over and over again.  However, it will use up more memory so it might be better
        to read the files depending on the purpose.
        """

        if self.data_dir is None:
            raise Exception('Name Creator requires the data directory to be set.')

        self._last_names    = self._file_reader(os.path.join(self.data_dir, self._last_file_name))
        self._female_names   = self._file_reader(os.path.join(self.data_dir, self._female_file_name))
        self._male_names     = self._file_reader(os.path.join(self.data_dir, self._male_file_name))


    def _file_reader(self, file_path):
        """
        Read the given file and store the "name" and 'cummulative score'
        :param file_name:
        :return: dict{'last': <last name>, 'first': <first name>}
        """


        data = {}
        data['names'] = []
        data['cumulatives'] = []
        with open(file_path) as fp:
            prev_cumulative_frequency = -1
            for line in fp:
                name, frequency, cumulative_frequency, rank, = line.split()
                data['names'].append(name)
                if int(prev_cumulative_frequency*1000) == float(cumulative_frequency)*1000:
                    # If the values match up to three decimal places then add .01 to the
                    # cumulative percentage
                    cumulative_frequency = prev_cumulative_frequency + 0.0001
                data['cumulatives'].append(float(cumulative_frequency))
                prev_cumulative_frequency = float(cumulative_frequency)

        return data


    def get_full_name(self, gender=None):
        """
        Generate a random name of the specified gender, if one is given.  Otherwised the
        gender is chosen randomly
        :param gender str: One of 'male', 'm', 'female', or 'f'
        :return: dict{ 'last', <last name>, 'first', <first name>}
        """
        if gender is None:
            gender = random.choice(('male', 'female'))

        if gender.lower() == 'female' or gender.lower() == 'f':
            gender = 'F'
        elif gender.lower() == 'male' or gender.lower() == 'm':
            gender = 'M'
        else:
            raise Exception('Invalid gender provided: ' + str(gender))

        assert(gender in ['F', 'M'])

        last_name = first_name = ''
        if self._last_names is None or self._female_names is None or self._male_names is None:
            last_name = self._get_name_from_file(os.path.join(self.data_dir, self._last_file_name))
            if gender == 'F':
                first_name = self._get_name_from_file(os.path.join(self.data_dir, self._female_file_name))
            else:
                first_name = self._get_name_from_file(os.path.join(self.data_dir, self._male_file_name))
        else:
            last_name = self._get_name_from_data(self._last_names)
            if gender == 'F':
                first_name = self._get_name_from_data(self._female_names)
            else:
                first_name = self._get_name_from_data(self._male_names)

        return { 'last': last_name,
                 'first': first_name}


    def _get_name_from_file(self, file_name):
        """
        Read the contents of the given file to find the name distribution.  From
        the distribution randomly pick a value.

        :param file_name: The file that is to be read for data

        :return [last_name, first_name]: The last name and first name that have been randomly selected
        """
        # TODO check the format of the file before reading the data
        names = []
        cumulative_scores = []
        with open(file_name) as fp:
            for line in fp:
                name, percentage, cumulative_percentage, rank = line.split()
                names.append(name)
                cumulative_scores.append(cumulative_percentage)

        max = float(cumulative_scores[-1])
        random_value = random() * max
        index = bisect(cumulative_scores, random_value)
        return names[index]

    def _get_name_from_data(self, data):
        """
        Obtain the random name for the list of names provided.
        :param data{}: Dictionary with two keys: 'names' and "cumulatives'
                       These lists are expected to be the same length.  The cumulative values
                       are the cumulative percentages read from the data file
        :return [last_name, first_name]: The last name and first name that have been randomly selected
        """
        names = data['names']
        cumulative_scores = data['cumulatives']

        max = float(cumulative_scores[-1])
        random_value = random() * max
        index = bisect(cumulative_scores, random_value)
        return names[index]


