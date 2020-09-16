#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
import sys, os, json

# Configuration for defining valid sheets and other default values
config = {
    ".warning": ["\033[93m", "\033[00m"], ".error": ["\033[91m", "\033[00m"],
    ".required": ["data_dictionary.json", "project.json", "sample.json"],
    "data_dictionary": {
        "input": "data_dictionary.json",
    },
    "project_template": {
        "input": "project.json",
    },
    "sample_template": {
        "input": "sample.json",
    }
}


def help():
        return """
initialize.py: Uses parsed data from lint.py to generate metadata JSON files.

USAGE:
    python initialize.py <lint_output_directory> <output_directory> [-h]

Required Positional Arguments:
    [1] lint_output_directory     Type [Path]: The output directory PATH provided in
                                  the previous step (lint.py). This path contains the
                                  parsed data catelogue along with parsed project-level
                                  and sample-level metadata (i.e. files listed below):
                                    + data_dictionary.json
                                    + project.json
                                    + sample.json

    [2] output_directory          Type [Path]: Absolute or relative PATH for output
                                  files. If the PATH does not exist, it will be
                                  automatically created during runtime.

Options:
    [-h, --help]                  Displays usage and help information for the script.

Example:
    $ python initialize.py /scratch/$USER/DME_Upload/ /scratch/$USER/DME_Upload/metadata/

Requirements:
    python >= 3.5
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
    if len(user_args) != 2:
        print("\n{}Error: Failed to provide all required arguments{}".format(*config['.error']), file=sys.stderr)
        print(help())
        sys.exit(1)

    return user_args


def path_exists(path):
    """Checks to see if output directory already exists or is accessible.
    If the PATH does not exist, it will attempt to create the directory and it's parent
    directories.
    """
    cstart, cend = config['.warning']

    if not os.path.isdir(path):
        print("{}WARNING:{} Output directory '{}' does not exist... creating it now!".format(cstart, cend, path), file=sys.stderr)
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


def validate(user_inputs):
    """Checks user input to see if file/directory exists or is accessible.
    If a file does not exist, the error is redirected to stderr and exits with
    exit-code 1. If a directory does not exist, it will attempt to create it.
    """

    required = config[".required"]
    ipath, opath = user_inputs
    file_w_path = []

    for file in required:
        file_exists(os.path.join(ipath, file))
        file_w_path.append(os.path.join(ipath, file))

    return file_w_path + user_inputs

def json2dict(file):
    """Reads in JSON file into memory as a dictionary. Checks to see if
    file exists or is accessible before reading in the file.
    """
    file_exists(file)

    with open(file, 'r') as f:
        data = json.load(f)

    return data

def separate(sep, extractions):
    """Extracts information from an existing dictionary and returns a list of
    seperate dictionaries.
    """
    extracted = []

    for k in extractions:
        tmp_d = {}
        tmp_d[k]=sep[k]
        extracted.append(tmp_d)

    return extracted


def generate(parsed_data, template, opath, helper):
    """Generates collection and data-object metadata needed for DME upload.
    For each collection (directory) and data-object (file), an output file is
    generated in JSON format. 'opath' dictates where these files will be saved.
    """
    template = json2dict(template)
    meta, fname = helper(parsed_data, template)

    # Saves upload metadata data as JSON file
    with open(os.path.join(opath, fname), 'w') as file:
        json.dump(meta, file, sort_keys=True, indent=4)

    return


def _pi(parsed_data, template):
    """Private helper function to generate(). Extracts metadata from parsed_data
    and adds it to the template, also returns new output filename for parsed metadata.
    """

    for k, metadict in parsed_data.items():
        for field, userdata in metadict.items():
            template['metadataEntries'].append({'attribute': field, 'value': userdata[0]})

    return template, 'pi_lab_collection.json'

def _project():
    pass


def main():

    # @args(): Parses positional command-line args
    # @validate(): Checks if user inputs are vaild
    data_dict, project_dict, sample_dict, ipath, opath = validate(args(sys.argv))

    # Read in JSON files as dictionary
    data_dict = json2dict(data_dict)
    pi_dict, project_dict = separate(json2dict(project_dict), ["PI_Lab", "Project"])
    sample_dict = json2dict(sample_dict)

    # Output directory for collection and data-object metadata
    path_exists(opath)

    # Get PATH to templates
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'data', 'templates')

    # Generate PI_Lab collection metadata
    generate(parsed_data=pi_dict, template=os.path.join(template_path, 'pi_lab_collection.json'), opath=opath, helper=_pi)


if __name__ == '__main__':

    main()
