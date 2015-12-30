#########################################################################
# FILE: pic_numbers.py
#
# DESCRIPTION:
# This file contains routines that manage files with iMIS numbers,
# Girl Guides of Canada eAccess numbers, maintained in a file or
# set of files.  This file is then used to randomly select 10
# iMIS numbers for a bi-monthtly newsletter.  The selected iMIS
# numbers win a prize.
#
# The file containing the iMIS numbers is a csv file in the following
# format:
#    Column  data type    description
#    0       integer      iMIS number, a 5-7 digit integer value
#    1       character    last name
#    2       character    first name
#    3       boolean      0 - not active member, 1 - active member
#    4       date         date the iMIS numbers was 1st selected
#    5       date         date the iMIS numbers was 2nd selected
#    6       date         date the iMIS numbers was 3rd selected
#    7       date         date the iMIS numbers was 4th selected
#
# date is a 8 digit integer in the format YYYYMMDD
#
#
# CREATION:
# Created by Shannon Jaeger, Sept 2014.
#
# TODO
# - Add command-line controls to switch modes (merging data, and selecting numbers)
# - Add command-line option to choose the number of selected iMIS numbers
# - Add command-line option to specify the input file(s)
# - Add command-line optinos to specify the output file
# - Investigate how worthwhile using a mini-db would be (SQLite perhaps)
# - Create classes for managing data, and selecting data possibly, could
#   be over-kill
#

import datetime;
import os;
import shutil;
import random;
import re;

#***********************************************************************#
#            Routines for selecting iMIS values                         #
#***********************************************************************#

##########################################################################
# NAME:  merge_files
#  
# DESCRIPTION:
# Takes two input files conataining iMIS numbers, one older and one with
# up-to-date information.  The contents of these two files are merged
# into a single set of iMIS numbers and written to a third file.
#
# The merging must follow these constraints:
#   1. Keep all iMIS numbers regardless of files
#   2. If an iMIS number doesn't appear in the up-to-date iMIS list
#      then the individual is no longer a member of the Alberta,
#      NWT, Yukon council and marked as inactive
#   3. Must maintain the date(s) that a number was selected.
#   4. If a number is not selected there are no dates associated with it
#
# INPUT:
#   Name       Data type    Description
#   filename1  string       up-to-date (new) file of iMIS numbers
#   filename2  string       old file of iMIS, selected iMIS numbers
#   filename3  string       name of the output file
#
# RETURN:
#   new_data   2D array     rows are members, columns match the
#                           expected columns in the output file.
# TODO
#   - Determine the new vs current working list from column headings.
#     New data won't have selected columns
#   - Produce errors when expected columns are not found
#   - modularize, remove the repitition in this function
#     and make it tinier
#   - allow the results to be optionally written to the old data
#     filename (ie. to filename2 if filename3 is not given)
def merge_files( filename1, filename2, filename3 ):
    f1_data = read_full_file( filename1 );
    f2_data = read_full_file( filename2 );

    # Find various column locations from column headings in the
    # new data file. If a heading isn't found the heading is
    # given a -1 value, the data we receive may or may not be
    # in a standard format.
    columns = f1_data['headings'];
    for i in range(0,len(columns) ):
        columns[i] = columns[i].lower();
        columns[i] = re.sub( '\s+', ' ', columns[i] ).strip();
        columns[i] = columns[i].replace('\r\n', '' );
        columns[i] = columns[i].replace('\n', '' );
        #print 'NEW HEADING : ' + columns[i];

    new_IMIS = -1;
    if ('id' in columns):
        new_IMIS = columns.index('id');
    elif ('imis'in columns ):
        new_IMIS = columns.index('imis');
    new_last_name = -1;
    if ( 'last name' in columns ):
        new_last_name = columns.index('last name');
    new_first_name = -1;
    if ('first name' in columns ):
        new_first_name = columns.index('first name');

    # Find various column locations from column headings in the
    # old data file, if a heading isn't found the heading is
    # given a -1, although if it isn't found then we probably
    # have a corrupt file
    columns = f2_data['headings'];
    for i in range(0,len(columns)):
        columns[i] = columns[i].lower();
        columns[i] = re.sub( '\s+', ' ', columns[i] ).strip();
        columns[i] = columns[i].rstrip('\r\n');
        columns[i] = columns[i].rstrip('\n');
        print 'NEW HEADING : ' + columns[i];

    old_IMIS = -1;
    if ('id' in columns ):
        old_IMIS = columns.index('id');
    elif ('imis' in columns ):
        old_IMIS = columns.index('imis'); # v
    print ', '.join( columns );

    old_last_name = -1;
    if ('last name' in columns ):
        old_last_name = columns.index('last name');

    old_first_name = -1;
    if ('first name' in columns ):
        old_first_name = columns.index('first name');

    old_active = -1;
    if ('active' in columns ):
          old_active = columns.index('active');

    # Extract the IMIS numbers from the new file and old file, ie. find
    # the list of numbers in each and create a set of new numbers if a
    # number appears in new or old then it will be in the new list.
    new_numbers = get_number_list( f1_data['member_data'], new_IMIS );
    old_numbers = get_number_list( f2_data['member_data'], old_IMIS );
    new_number_list = new_numbers + old_numbers;
    new_number_list = list(set(new_number_list));
    new_number_list.sort();

    # Create the new data array with the following columns:
    # IMIS, Last Name, First Name, Active, selected1, selected2, selected3, selected 4
    #
    # We first try and find the information in the "new" data assuming it is
    # the most up-to-date then look for it in the old one, note if the field
    # doesn't appear in the new data, the member has gone inactive.
    data = [];
    new_data = f1_data['member_data'];
    old_data = f2_data['member_data'];
    for i in range(0, len(new_number_list) ):
        new_row = [];

        # Find the index into the old and new data arrays to
        # save us from doing this over and over.  If the current
        # iMIS number being processed isn't in the list the indes
        # value is given a value of -1;
        new_row.append( str(new_number_list[i]) );

        new_i = -1;
        if ( int(new_row[0]) in new_numbers ):
            new_i = new_numbers.index(int(new_row[0]));

        old_i = -1;
        if ( int(new_row[0]) in old_numbers ):
            old_i = old_numbers.index(int(new_row[0]));
            

        #print "Creating row " + str(i) + ' IMIS ' + new_row[0] + ' in old ' + str(old_i) + ' in new ' + str( new_i );

        # Find the name associated with the iMIS number
        if ( new_i >= 0 and new_last_name >= 0 ):
            new_row.append( new_data[new_i][new_last_name] );
        elif (old_i >= 0 and  old_last_name >= 0 ):
            new_row.append( old_data[old_i][old_last_name] );
        else:
            new_row.append( "" );

        if ( new_i >= 0 and new_first_name >= 0 ):
            new_row.append( new_data[new_i][new_first_name] );
        elif ( old_i >= 0 and old_first_name >= 0 ):
            new_row.append( old_data[old_i][old_first_name] );
        else: 
            new_row.append( "" );

        # IF new_i >= 0 then the member is active
        if ( new_i >= 0 ):
            new_row.append( '1' );
        else:
            new_row.append( '0' );

        # Add all the dates that the member was selected
        if ( old_i >= 0 ):
            print 'OLD DATA ' +  ', '.join(old_data[old_i]);
            for j in range(1, 5):
                if (old_active+j < len(old_data[old_i]) ):
                    value = (old_data[old_i][old_active+j]).replace('\n', '');
                    print 'found ' + repr(value);
                    new_row.append( value );
                else:
                    print 'not found';
                    new_row.append( "" );
        else:
            print 'NEW DATA ' +  ', '.join(new_data[new_i]);
            for j in range(1, 5):
                new_row.append( "" );            
        data.append(new_row);

    # Write the data to the "merge file"
    fp = open( filename3, 'w');
    fp.write('IMIS,Last Name,First Name,Active,Selected 1,Selected 2,Selected 3,Selected 4\r\n');
    fp.write(',,,,,,,\r\n');
    for i in range(0, len(data) ):
        fp.write(','.join(data[i]) + '\r\n' );
    fp.close();
                
    return new_data;


#########################################################################
# NAME: read_full_file
#
# DESCRIPTION:
# read a csv file and store the information read into a data
# dictionary.  It's assumed that the first row contains the headings
# of the columns, the data follows.       
#
# INPUT:
#   filename    string         Name of the file to read
#
# RETURN:
#   ??      data dictionary    {'headings': data, 'member_data': data }      
#
# TODO:
#  - throw an exception if there is an error opening the file.
#  - Change function name to read_csv_file
#  - Change return data dict to have fields: heading and data
#  - skip blank lines.
def read_full_file (filename):
    column_headings = [];
    data = [];

    # TODO 
    fp = open( filename, 'rU' );
    for line in fp:
        line_list = line.split(',');
        if ( not line_list[0].isdigit() ):
            # Either blank line or column headings
            if ( len(line_list) > 1 ):
                column_headings = line_list;
        else:
            # It is data 
            data.append(line_list);

    fp.close();
    return { 'headings': column_headings, 'member_data': data };

# Get the list of IMIS numbers from complete file
# information
def get_number_list( file_data, column ):
    number_list = [];
    for i in range(0, len(file_data ) ):
         if (len(file_data[i][column]) > 0 and file_data[i][column].isdigit() ):
            number_list.append( int(file_data[i][column]) );

    return number_list;


#***********************************************************************#
#            Routines for selecting iMIS values                         #
#***********************************************************************#
                   
#########################################################################
# NAME: read_data_file
#
# DESCRIPTION:
# Read the most current file with iMIS numbers, names, and selection
# dates and store in an data structure that is easy to use for selecting
# iMIS numbers.  Only the active members are returned, the inactive ones
# are ignored.  
#
# INPUT:
#   filename    string    Name of the input file. The data in the file
#                         is assumed to be a csv file in the following format:
#
#                        iMIS, Last Name, First Name, Active , date(s) Picked
#                          0,      1   ,     2     ,   3    , 4, 5, 6, 7
#
# RETURN:
#   ??       data dictionary   { 'members': x, 'selected', y, 'inactive', z}
#                 'members':  2D array, each row is an active member
#                             each row contains the columns listed for the
#                             input file
#                 'selected': integer, number of iMIS numbers that have a
#                             date in at least one of the selection date fields
#                 'inactive': integer, number of inactive members found
#
# TODO
#   - Add debugging that can be turned on and off
#   - Error handling, such as an exception if file is not found or
#     there is an error in the data
#   - skip blank lines
#   - return/collect the number of inactive members that have been 
#     selected and possibly other intriguing data
#   - make it more generic by using column headings to determine
#     the data order
def read_data_file( filename ):
    # initialize the data structures to be returned.
    data_array 		= [];
    selected 		= 0;
    inactive 		= 0;
    inactive_selected	= 0;
    num_lines 		= 0;

    fp = open( filename, 'rU' );
    for line in fp:
        num_lines +=1;
        line_list = line.split(',');
        if (not line_list[0].isdigit() ):
            # Not member information skip it
            #print "SKIPPING LINE: " + line;
            continue;
        if ( len(line_list[3]) > 0 and line_list[3] == '0' ):
            # Inactive member, don't store this one
            inactive += 1;
            #print "INACTIVE LINE: " + line;
            if (len (line_list[4]) > 0 ):
                inactive_selected += 1;
            continue;
        if (len (line_list[3]) < 0 ):
            # Not marked so we assume active, although this should occur
            # only the very first time this application is run.
            line_list[3] = '1';
        if ( len(line_list[4]) > 0 ):
            # We have found someone that has already been picked yet.
            selected += 1;

        # If we made it this far the row is an active member that
        # we may choose to select.
        data_array.append(line_list);

    #print 'READ ' + str(num_lines) + ' lines';
    fp.close();
    return { 'members': data_array, 
             'selected': selected,
             'inactive': inactive,
             'inactive_selected': inactive_selected };

#########################################################################
# NAME: select_numbers
#
# DESCRIPTION:
# select a set of iMIS numbers from the list of active members that are
# in the data provided.  
#
# INPUT:
#   file_data    	dict      Data results from read_data_file function
#   number_to_select    int       Number of numbers to select
#
# Each member is a row in the file_data['members'] with the following data:
# IMIS, Last Name, First Name, Active , date(s) Picked
#   0 ,      1   ,     2     ,   3    , 4, 5, 6, 7
#
# RETURN:
#   selected_members    array     List of indicies into the file_data['memmbers']
#                                 array indicating those that have been
#                                 selected.
#
# TODO:
#  - Update the selection process to skip over "inactive" members so
#    that the full file data can be written out.
#  - Ability to turn debugging on and of
#  - Update the algorithm to select a member if they've already been
#    selected "x" number of times if "y" percentage of members have
#    been selected "x-1" times.  At the moment this is not needed since
#    many members have not been selected of times.
#
def select_members( file_data, num_to_select ):
    member_data		 = file_data['members'];
    num_members 	 = len(member_data);
    count		 = 0;
    selected_members	 = [];

    random.seed();
    random.randrange(0, num_members );
    while ( count < num_to_select ):
        # Keep looking for members (iMIS number) until we have the number
        # of numbers we are looking for.
        new_idx = random.randint(0, num_members);
        if ( len(member_data[new_idx][4]) < 1 ):
            # It's a number that hasn't been selected before woohoo!
            # We select this one.
            selected_members.append( new_idx );
            #print 'selected %d \n' % new_idx;
            count += 1;
    return selected_members;

#########################################################################
# NAME: print_selected_members
#
# DESCRIPTION:
# A very tiny routine that prints out who is selected
#
# INPUT: list of selected indicies, file_data that was read
#
# TODO
#   - add options defining what is printed out, alhtough that's likely
#     overkill for this application
#
def print_selected_members( selected_indicies, data ):
    for idx in selected_indicies:
        print "%8s %s %s" % (data[idx][0], data[idx][2], data[idx][1]);

#########################################################################
# NAME: update_member data
#
# DESCRIPTION
# Update the data to add today's date to the members list of dates that
# they've been selected.
#
# INPUT:
#   selected_indicies   list        The indicies into the data that are
#                                   the members that were just selected
#   data                2D array    The member data that was read from
#                                   the input file
# RETURN:
#   data                2D array    the member data that was read from the
#                                   input file with updated selection dates
#                                   The date is in YYYYMMDD format.
#
# TODO:
# - It is assumed that the member has never been selected before
#    and adding todays date to the first "selected" column, but if there
#    is a date in this column it needs to be put into the second "selected"
#    column and so on.  This is sufficient for now as only never previously
#    selected members will be selected
#
def update_member_data( selected_indicies, data ):
    today = datetime.date.today();
    today_str = "%4d%02d%02d" % (today.year, today.month, today.day);

    for idx in selected_indicies:
        data[idx][4] = today_str;
    return data;

#########################################################################
# NAME: update_imis_file
#
# DESCRIPTION:
# write the updated information, with selected iMIS numbers, to an output
# file.
#
# INPUT:
#   filename       string     Path to the file that is to contain the
#                             updated information.
#   data           2D array   An array containing the data related to
#                             the members.
# RETURN:
#   None
#
# TODO:
#   - Throw an exception if an error opening or writing to the file
#     occurs.
#   - Include in the "inactive" members in the output information.
def update_imis_file( filename, data ):
    shutil.copyfile( filename, filename+'.bak' );
    os.remove( filename );

    fp = open( filename, 'w' );
    fp.write('IMIS,Last Name,First Name,Active,Selected 1,Selected 2,Selected 3,Selected 4');
    fp.write(',,,,,,,');
    for i in range(0, len(data)):
        fp.write( ','.join(data[i]) );
    fp.close();

#***********************************************************************#
#                          Main function                                #
#***********************************************************************#

# This section needs to be put into a function and use command-line
# option values, rather then hard-coded values.  Also need to have
# two modes, select numbers and merge data instead of turning bits
# of the code on or off.
#


## ToDo, use the current date to determine which file to read
##       and/or command-line args to determin if merging or
##       selecting numbers, might want a test mode
year 		= '2015';
month       = 'Nov';
day		    = '23';
imis_filename 	= './iMIS_numbers_'+ month + day + year+'.csv';

if True == True:
    file_data 	= read_data_file( imis_filename );
    total_active	= int(len(file_data['members']));
    amount_to_pick 	= 10;

    print 'Total number of Members:                %d' % (total_active + file_data['inactive']);
    print 'Number of Active Members:               %d' % total_active;
    print 'Number of Inactive Members:             %d' % file_data['inactive'];
    print 'Number of Inactive Selected Members:    %d' % file_data['inactive_selected'];
    print 'Number of Unselected Members:           %d' % (total_active - file_data['selected']);
    print 'Number of Selected Members:             %d' % file_data['selected'];

    selected_idxs = select_members( file_data, amount_to_pick );
    print_selected_members( selected_idxs, file_data['members'] );
    updated_data = update_member_data( selected_idxs, file_data['members'] );
    update_imis_file( imis_filename, updated_data );

if True == False:
    merge_files( 'iMISNumbersOct2015.csv', 'iMIS_numbers_Oct132015.csv',  'iMIS_numbers_Oct132015Merged.csv');


