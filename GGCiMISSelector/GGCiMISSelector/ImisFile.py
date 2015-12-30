__author__ = 'shannonjaeger'

from Exceptions import *
import csv



class Member(object):
    def __init__(self, imis, first_name=None, last_name=None, active=False, dates_selected=[]):
        try:
            assert(isinstance(imis, int))
            self.imis = imis
        except:
            self.imis = int(imis)

        try:
            assert(isinstance(active, bool))
            self.active = active
        except:
            self.active = bool(active)

        if isinstance(dates_selected, list):
            self.dates_selected = dates_selected
        elif isinstance(dates_selected, str):
            self.dates_selected = dates_selected.split(':')

        self.first_name = str(first_name)
        self.last_name = str(last_name)
        self.dates_selected = dates_selected

    def as_list(self):
        active = '1' if self.active else '0'
        return [ str(self.imis), self.last_name, self.first_name, active, self.dates_selected]

    def getKey(self):
        return  str(self.active)+':'+self.last_name+':'+self.first_name

    def __cmp__(self, other):
        if hasattr(other, 'getKey'):
            return self.getKey().__cmp__(other.getKey())

    def __eq__(self, other):
        return self.imis == other.imis

    def __ne__(self, other):
            return self.last_name.lower() != other.last_name.lower() \
                 or self.first_name.lower() != other.first_name.lower()

    def __lt__(self, other):
        if self.active != other.active and self.active:
            return False
        elif self.active != other.active:
            return True
        elif self.last_name.lower() != other.last_name.lower():
            return self.last_name.lower() < other.last_name.lower()
        else:
            return self.first_name.lower() < other.first_name.lower()

    def __gt__(self, other):
        if self.active != other.active and not self.active:
            return False
        elif self.active != other.active:
            return True
        elif self.last_name.lower() != other.last_name.lower():
            return self.last_name.lower() > other.last_name.lower()
        else:
            return self.first_name.lower() > other.first_name.lower()

    def __le__(self, other):
        if self.active != other.active and self.active:
            return False
        elif self.active != other.active:
            return True
        elif self.last_name.lower() != other.last_name.lower():
            return self.last_name.lower() <= other.last_name.lower()
        else:
            return self.first_name.lower() <= other.first_name.lower()

    def __ge__(self, other):
        if self.active != other.active and not self.active:
            return False
        elif self.active != other.active:
            return True
        elif self.last_name.lower() != other.last_name.lower():
            return self.last_name.lower() >= other.last_name.lower()
        else:
            return self.first_name.lower() >= other.first_name.lower()

    def __str__(self):
        return '{0} {1: >8}: {2: >20} {3: >15} - {4}'.format(str(self.active),
                                                             str(self.imis),
                                                             self.last_name,
                                                             self.first_name,
                                                             self.dates_selected)




class ImisFile():
    """
    read, write and merge csv files containing iMIS information.

    Attributes:

    """


    def __init__(self, file_path=None):
        self.imis_header = 'iMIS'
        self.last_name_header = 'Last Name'
        self.first_name_header = 'First Name'
        self.active_header = 'Active'
        self.dates_selected_header = 'Dates Selected'

        self.active_member_list = []
        self.inactive_member_list = []
        self.num_active_selected = 0
        self.num_inactive_selected = 0

        self.file_path = None
        if file_path is not None:
            self.set_file_path(file_path)
            self.read()

    def set_file_path(self, file_path):
        """
        Set the file path to be read/written from
        :param file_path: A fully specified file path on the file system to an iMIS data file.
        :return: None
        """
        # Do our variable sanity checks
        assert(file_path is not None)

        self.file_path = file_path

    def get_file_path(self):
        """
        Return the file path being used.
        :return: The fully specified path where data is written/read from.
        """
        return self.file_path


    def _parse_headings(self, headings):
        """
        Find which column the various potential headers are in the given set of
        headings.  Note that only the iMIS number is the only column that must be
        there.
        :param headings: the headings as a list
        :return heading_columns:
        """
        import re

        heading_columns = {'imis': -1,
                       'last_name': -1,
                       'first_name': -1,
                       'active': -1,
                       'dates_selected': -1
        }

        for i in range(0,len(headings)):
            headings[i] = headings[i].lower();
            headings[i] = re.sub('\s+', ' ', headings[i] ).strip()
            headings[i] = headings[i].replace('\r\n', '')
            headings[i] = headings[i].replace('\n', '')

        for key in heading_columns.keys():
            search_item = key.lower().replace('_', ' ')
            heading_columns[key] = headings.index(search_item) if search_item in headings else -1

        if heading_columns['imis'] == -1:
            raise InvalidImisFile('File "{0}" does not have an iMIS number column.'.format(str(self.file_path)))

        return heading_columns


    def read(self):
        """
        Read CSV file containing iMIS numbers with or without names, and with or without
        The data columns are expected to be in the following order:
            iMIS Number
            Last Name
            First Name
            Membership Activity Status
            Selection Dates

        If the file is successfully read a list of active and inactive members is
        created.

        :return None:
        """

        if self.file_path is None:
            raise NoImisFile("An iMIS file path has not been provided.")

        column_locations = {}
        with open(self.file_path, 'rU') as fp:
            reader = csv.reader(fp, delimiter=",", quoting=csv.QUOTE_NONE)
            for line in reader:
                if len(column_locations) < 1:
                    column_locations = self._parse_headings(line)
                    continue

                if len(line) < 1: continue # Empty line

                if not line[column_locations['imis']].isdigit():
                    # No iMIS number on line so skip it
                    # TODO verify this is not an error
                    continue

                # If we've made it here we have a new member!
                new_member = Member(imis=line[column_locations['imis']])

                new_member.first_name = line[column_locations['first_name']] \
                        if column_locations['first_name'] != -1 else ''
                new_member.last_name = line[column_locations['last_name']] \
                        if column_locations['last_name'] != -1 else ''
                new_member.active = bool(line[column_locations['active']]) \
                        if column_locations['active'] != -1 else True
                new_member.dates_selected = line[column_locations['dates_selected']] \
                        if column_locations['dates_selected'] != -1 else ''

                # Now lets add this member to the active or inactive member list
                # TODO if a duplicate is found make sure to not lose any data
                if new_member.active and new_member not in self.active_member_list:
                    self.active_member_list.append(new_member)
                elif not new_member.active and new_member not in self.inactive_member_list:
                    self.inactive_member_list.append(new_member)


    def _get_default_header_(self, ):
        """
        The default headers ...
           iMIS, Last Name, First Name, Active, Dates Selected
        :return: the header strings in a list
        """
        return [self.imis_header, self.last_name_header, self.first_name_header,
                    self.active_header, self.dates_selected_header]


    def write(self, file_path=None):
        """
        Write the inactive and active member lists to a file.
        :param file_path: The path to the file where the data is to be written.
        :return: None
        """

        if file_path is None and self.file_path is None:
            raise NoImisFile('A file path for the iMIS data must be specified before the data can be written.')
        if file_path is None:
            file_path = self.file_path

        full_list = self.active_member_list + self.inactive_member_list
        #sorted_list = sorted(full_list)

        with open(file_path, 'w') as fp:
            csv_writer = csv.writer( fp, delimiter=",", quoting=csv.QUOTE_NONE)
            csv_writer.writerow(self._get_default_header_())
            for member in full_list:
                csv_writer.writerow(member.as_list())


    def merge(self, new_file_obj):
        """
        Merge this iMIS file object with a new file.  It is assumed that the new
        file contains a complete list of the current active members.  It is the
        Provincial Council Membership list of current members only.

        After the merge the internal data structures will contain the "merged"
        data, each iMIS number will appear on either the active or inactive list
        exactly once.

        :param new_file (str/ImisFile): If it is a string then it's assumed to be a
        fully specified file path, if it is an ImisFile object who's file_path has
        been set.
        :return: True if the merge was successful, False otherwise
        """
        if self.file_path is  None:
            raise NoImisFile('Must set ')

        new_file = ImisFile()
        if isinstance(new_file_obj, str):
            # new_file is a file_path
            new_file.set_file_path(new_file_obj)
        elif new_file_obj.__class__ == ImisFile:
            # nothing to do
            pass
        else:
            raise ValueError('file_path must be a string or ImisFile type.')

        # If we haven't read in the files then read them in
        if len(self.inactive_member_list) == 0 and len(self.active_member_list) == 0:
            self.read()
        if len(new_file.inactive_member_list) == 0 and len(new_file.active_member_list) == 0:
            new_file.read()


        # Mark all of the old (self) active members as inactive
        for member in self.active_member_list:
            member.active = False
            self.inactive_member_list.append(member)
        self.active_member_list=[]

        # Go through the active member list from the new_file.  If a member
        # is found in the inactive list then move this member to the active
        # member list. Note that any dates that the members iMIS number was
        # selected will be in the old data
        new_file.active_member_list.sort()
        for new_member in new_file.active_member_list:
            try:
                pos = self.inactive_member_list.index(new_member)
                old_member = self.inactive_member_list.pop(pos)
            except ValueError:
                # The member isn't in the list
                old_member = None

            # Update the old member to active and verify the name
            old_member.active = True
            if len(new_member.last_name) > 0 \
                    and new_member.last_name != old_member.last_name:
                old_member.last_name = new_member.last_name
            if len(new_member.first_name) > 0 \
                    and new_member.first_name != old_member.first_name:
                old_member.first_name = new_member.first_name

            self.active_member_list.append(old_member)

        self.inactive_member_list = self.inactive_member_list + new_file.inactive_member_list
        self.inactive_member_list.sort()



