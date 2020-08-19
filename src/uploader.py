#!/usr/bin/env python
from __future__ import print_function, division
import sys, os, re
import pandas as pd

# Configuration for defining valid sheets and other default values
config = {
    ".warning": ["\033[93m", "\033[00m"], ".error": ["\033[91m", "\033[00m"],
    ".sheets": ["Data Dictionary", "Project Template", "Sample Template"]
}


def help():
        return """
USAGE:
    python uploader.py <project_request_spreadsheet> <output_directory> [-h]

    Positional Arguments:
    [1] project_request_sheet     Type [File]: A filled out project request out form.
                                  This spreadsheet is sent out to the PI or post-doc
                                  that is requesting our assistance. Please see
                                  "data/experiment_metadata.xlsx" as an example.

    [2] output_directory          Type [Path]: Absolute or relative PATH for output
                                  files. If the PATH does not exist, it will be
                                  automatically created during runtime.

    Optional Arguments:
    [-h, --help]  Displays usage and help information for the script.

    Example:
    $ python uploader.py data/experiment_metadata.xlsx /scratch/$USER/DME_Upload/

    Requirements:
    python >= 2.7
      + pandas
      + xlrd
"""


def args(argslist):
    """Parses command-line args from "sys.argv". Returns a list of args to parse."""
    # Input list of filenames to parse
    user_args = argslist[1:]

    # Check for optional args
    if '-h' in user_args or '--help' in user_args:
        print(help())
        sys.exit(0)
    # Check to see if user provided input files to parse
    elif len(user_args) != 2:
        print("\n{}Error: Failed to provide all required arguments{}".format(*config['.error']), file=sys.stderr)
        print(help())
        sys.exit(1)

    return user_args


def path_exists(path):
    """Checks to see if output directory already exists or is accessible.
    If the PATH does not exist, it will attempt to create the directory and it's parent
    directories.
    """
    if not os.path.isdir(path):
        print("\n{}WARNING: Provided output directory does not exist!{}".format(*config['.warning']), file=sys.stderr)
        print("Creating output directory {}".format(path), file=sys.stderr)
        try:
            os.makedirs(path)
        except OSError as e:
            cstart, cend = config['.error']
            print("{}Error:{} Failed to create {}... PATH not accessible!\n{}".format(cstart, cend, path, e), file=sys.stderr)
            sys.exit(1)
    return


def file_exists(filename):
    """Checks to see if file exists or is accessible.
    Avoids problem with inconsistencies across python2.7 and >= python3.4 and
    works in both major versions of python"""
    try:
        fh = open(filename)
        fh.close()
    # File cannot be opened for reading (may not exist) or permissions problem
    except IOError as e:
        cstart, cend = config['.error']
        print("{}Error:{} Failed to open {}... Input file not accessible!\n{}".format(cstart, cend, filename, e), file=sys.stderr)
        sys.exit(1)
    return

def contains_sheets(spreadsheet):
    """Checks to see if user-provided spreadsheet contains all the required sheets
    that are defined in the config specification. Please see config['.sheets']
    for all required sheets.
    """

    required = config['.sheets']
    df = pd.read_excel(spreadsheet, sheet_name=None, header=None)
    valid_sheets = [sheet for sheet in df.keys() if sheet in required]

    if sorted(valid_sheets) != sorted(required):
        # Required sheet not in spreadsheet
        missing = set(required) - set(valid_sheets)
        raise Exception('Spreadsheet is missing the following sheet(s): {}'.format(missing))
        sys.exit(1)

    return valid_sheets

def validate(user_inputs):
    """Checks user input to see if file/directory exists or is accessible.
    If a file does not exist, the error is redirected to stderr and exits with
    exit-code 1. If a directory does not exist, it will attempt to create it.
    """

    meta_sheet, output_path = user_inputs
    file_exists(meta_sheet)
    path_exists(output_path)
    sheets = contains_sheets(meta_sheet)

    return meta_sheet, output_path, sheets

def data_dictionary():
    """
    """
    pass
    
def main():

    # @args(): Parses positional command-line args
    # @validate(): Checks if user inputs are vaild
    metadata, opath, sheets = validate(args(sys.argv))

    # Generate Data Dictionary






if __name__ == '__main__':

    main()
