#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
import sys, os, json, re

# Configuration for defining valid sheets and other default values
config = {
    ".warning": ["\033[93m", "\033[00m"], ".error": ["\033[91m", "\033[00m"],
    ".required": ["data_dictionary.json", "project.json", "sample.json"],
    ".vaults": ["CCBR_Archive", "CCBR_EXT_Archive"],
    "data_dictionary": {
        "input": "data_dictionary.json",
    },
    "project_template": {
        "input": "project.json",
        "singularity_required": ["project_title", "project_description",
                                  "start_date", "project_poc","poc_email"],
    },
    "sample_template": {
        "input": "sample.json",
    }
}


def help():
        return """
initialize.py: Instantiates or updates DME project collection heirarchy

USAGE:
    python initialize.py <lint_output_directory> <output_directory> <dme_vault> [-h]

SYNOPSIS:
    Uses parsed data (or output) from 'lint.py' to generate metadata JSON files
for DME collection initialization. User must provide the output directory of 'lint.py',
a path for newly generated ouput files, and select from one of the following DME vaults
to initalize or update a project: 'CCBR_EXT_Archive', 'CCBR_Archive'.

    'CCBR_EXT_Archive' is for storing/archiving data from public repositories like GEO,
SRA, dbGap, EBI. 'CCBR_Archive' is for storing/archiving from external vendors like
Novogene, ACGT, Macrogen, Genentech, GeneDx, CCR Genomics Core, NISC, SCAF, or COMPASS.

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

    [3] dme_vault                 Type [String]: DME vault to store data and metadata.
                                  Valid choices are 'CCBR_EXT_Archive' or 'CCBR_Archive'.
                                  NOTE:
                                    @ 'CCBR_EXT_Archive' is for public datasets.
                                    @ 'CCBR_Archive' is data from outside vendors.

Options:
    [-c, --convert]               Type [Boolean]: Provide flag if field names need
                                  to be converted into DME format.

    [-h, --help]                  Displays usage and help information for the script.

    [-p, --project-id]            Type [String]: Optional Project ID. This could be a
                                  ccbr project id if it has been assigned a project or
                                  a NAS request id.
                                  Example: 'ccbr-123'
    [-m, --sample-metdata]        Type [File]: Optional TSV file containing additional sample
                                  metadata. This analysis-specific, quality-control metadata
                                  is calculated for each sample by aggregating MultiQC output.
                                  Example: 'multiqc_matrix.tsv'
    [-a, --analysis-metdata]      Type [File]: Optional TSV file containing analysis
                                  metadata. The metadata in this file is used to instantiate
                                  a Primary Analysis collection. It contains information about
                                  the pipeline and its inputs.
                                  Example: 'runinfo.txt'

Example:
    $ python initialize.py /scratch/DME/ /scratch/DME/metadata/ CCBR_EXT_Archive -c

Requirements:
    python >= 3.5
"""


def args(argslist):
    """Parses command-line args from "sys.argv". Returns a list of args to parse."""
    # Input list of filenames to parse
    user_args = argslist[1:]
    convert = False
    project_id = ''
    metafile = ''
    analysisfile = ''

    # Check for optional args
    if '-h' in user_args or '--help' in user_args:
        print(help())
        sys.exit(0)

    # Check for convert boolean flag
    if '-c' in user_args or '--convert' in user_args:
        print('Converting field names to dme field format.')
        user_args = [arg for arg in user_args if arg not in ['-c', '--convert']]
        convert = True

    # Check for optional Project ID
    if '-p' in user_args or '--project-id' in user_args:
        for i in range(len(user_args)):
            if user_args[i] in ['-p', '--project-id']:
                option_index = i
                try:
                    project_id = user_args[option_index+1]
                except IndexError:
                    print("\n{}Error: Failed to provide a value to '-p' argument{}".format(*config['.error']), file=sys.stderr)
                    sys.exit(1)
                break
        user_args = [arg for arg in user_args if arg not in ['-p', '--project-id', project_id]]

    # Check for optional sample metadata
    if '-m' in user_args or '--sample-metadata' in user_args:
        for i in range(len(user_args)):
            if user_args[i] in ['-m', '--sample-metadata']:
                option_index = i
                try:
                    metafile = user_args[option_index+1]
                except IndexError:
                    print("\n{}Error: Failed to provide a metadata file to '-m' argument{}".format(*config['.error']), file=sys.stderr)
                    sys.exit(1)
                break
        user_args = [arg for arg in user_args if arg not in ['-m', '--sample-metadata', metafile]]

    # Check for optional piprline or analysis metadata
    if '-a' in user_args or '--analysis-metadata' in user_args:
        for i in range(len(user_args)):
            if user_args[i] in ['-a', '--analysis-metadata']:
                option_index = i
                try:
                    analysisfile = user_args[option_index+1]
                except IndexError:
                    print("\n{}Error: Failed to provide a metadata file to '-a' argument{}".format(*config['.error']), file=sys.stderr)
                    sys.exit(1)
                break
        user_args = [arg for arg in user_args if arg not in ['-a', '--analysis-metadata', analysisfile]]

    # Check to see if user provided input files to parse
    if len(user_args) != 3:
        print("\n{}Error: Failed to provide all required arguments{}".format(*config['.error']), file=sys.stderr)
        print(help())
        sys.exit(1)

    return [project_id.upper(), metafile, analysisfile, convert] + user_args


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
    valid_vaults = config[".vaults"]

    pid, metafile, analysisfile, convert, ipath, opath, vault = user_inputs
    file_w_path = []

    assert vault in valid_vaults, "{} is not a vaild DME vault! Please choose from one of the following: {}".format(vault, valid_vaults)

    for file in required:
        file_exists(os.path.join(ipath, file))
        file_w_path.append(os.path.join(ipath, file))

    # Check file optional metadata file actually exists
    if metafile:
        file_exists(metafile)
    if analysisfile:
        file_exists(analysisfile)

    return file_w_path + user_inputs


def field2DME(data, data_catelog):
    """Converts common field names with dme field names. Returns a dictionary of
    converted names suitable for archiving.
    """
    converted = {}

    for collection_type, metadict in data.items():
        if collection_type not in converted:
            converted[collection_type] = {}
        for common_name, user_value in metadict.items():
            try:
                dme_name = data_catelog[collection_type][common_name][0]
            except KeyError: # sample dict key is sample_id and not collection type
                dme_name = data_catelog['Sample'][common_name][0]
            converted[collection_type][dme_name] = user_value

    return converted


def mqc2dict(file, ignore=[0,-1]):
    """Reads in MultiQC TSV file into memory as a dictionary while ignore specific indices.
    Checks to see if file exists or is accessible before reading in the file.
    where dict[sample] = [{attr: value}, {}, ...]
    """
    file_exists(file)
    metadata = {}

    with open(file, 'r') as f:
        header = next(f).split('\t')
        # Ignore First and Last Fields
        for i in ignore: header.pop(i)
        for line in f:
            linelist = line.split('\t')
            sample = linelist[0]

            # Ignore First and Last Fields
            for i in ignore: linelist.pop(i)
            if sample not in metadata:
                metadata[sample] = []
            for i in range(len(linelist)):
                 metadata[sample].append({"attribute": header[i], "value": linelist[i]})

    return metadata


def tsv2dict(file, key_index = 0, value_index = 1, header = False):
    """Reads in Run TSV file into memory as a dictionary.
    Checks to see if file exists or is accessible before reading in the file.
    where dict[key_index] = value_index
    """
    file_exists(file)
    metadata = {}
    samples = []

    with open(file, 'r') as f:
        if header:
            header = next(f).split('\t')
        for line in f:
            linelist = line.rstrip('\n').split('\t')
            dme_attribute = linelist[key_index]

            # Check for edge-case where value DNE
            try: dme_value = linelist[value_index]
            except IndexError: dme_value = "Unknown"

            if dme_attribute == 'file':
                samples.append(dme_value)
                continue

            metadata[dme_attribute] = dme_value

    samples = sorted([re.split('\.R[12]\.fastq\.gz', os.path.basename(s))[0] for s in set(samples)])
    samples = ",".join(samples)

    # iRODS VARCHAR limit is 2700
    # Add input_samples_list dme attribute if less than 2700 characters
    if len(samples) < 2700:
        metadata['input_samples_list'] = samples

    return metadata


def json2dict(file):
    """Reads in JSON file into memory as a dictionary. Checks to see if
    file exists or is accessible before reading in the file.
    """
    file_exists(file)

    with open(file, 'r') as f:
        data = json.load(f)

    return data


def dict2list(mydict, mylist, i, override_index=[]):
    """Given a dictionary, and a list of keys of interest, it will return a list
    of values. Parameter 'i' can be overrided to default to 0 using override_index.
    """
    values_list = []
    for k, metadict in mydict.items():
         #values_list = [metadict[v][i] for v in mylist ]
         for v in mylist:
             index = i
             if v in override_index:
                 index = 0

             values_list.append(metadict[v][index])

    return values_list

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


def generate(parsed_data, template, opath, dme_vault, helper, **kwargs):
    """Generates collection and data-object metadata needed for DME upload.
    For each collection (directory) and data-object (file), an output file is
    generated in JSON format. 'opath' dictates where these files will be saved.
    Returns a dictionary of collection information where [key]= DME PATH of
    the collection to initialized or updated and [value] = abolute PATH of the
    collection metadata json file.
    """
    template = json2dict(template)
    collections = helper(parsed_data, template, opath, dme_vault, **kwargs)

    return collections


def _pi(parsed_data, template, opath, dme_vault, index=0):
    """Private helper function to generate(). Extracts PI_Lab metadata from parsed_data,
    adds it to the template, and writes it to a new file. Returns a dictionary containing
    collection information where [keys] are collection_name and values are the output
    filename for parsed metadata. The relationship between each project request to
    PI_Lab collection(s) is '1:1'.
    """

    for k, metadict in parsed_data.items():
        for field, userdata in metadict.items():
            template['metadataEntries'].append({'attribute': field, 'value': userdata[0]})

    # Get name and aff for output
    name, aff = dict2list(parsed_data, ["pi_name", "affiliation"], i=index)
    last, first = [n.lstrip().rstrip() for n in name.split(',')]
    aff = aff.split()[-1].replace('(','').replace(')','')
    collection_name = 'PI_Lab_{}{}_{}'.format(first, last, aff)

    outfile = os.path.join(opath, '{}.metadata.json'.format(collection_name))
    path_exists(os.path.join(opath, '{}'.format(collection_name)))

    # Save upload collection metadata data as JSON file
    with open(outfile, 'w') as file:
        json.dump(template, file, sort_keys=True, indent=4)

    return {collection_name: outfile}


def _project(parsed_data, template, opath, dme_vault, pid):
    """Private helper function to generate(). Extracts Project metadata from parsed_data,
    adds it to the template, and writes it to a new file. Returns a dictionary containing
    collection information where [keys] are collection_name and values are the output
    filename for parsed metadata. The relationship between each project request to
    Project collection(s) is '1:M' (multiple sub-projects, i.e. RNA-seq and ATAC-seq).
    """
    subcollections = {}
    subprojects = parsed_data["Project"]["request_type"]
    singular_fields = config["project_template"]["singularity_required"]

    for i in range(0, len(subprojects), 1):
        temp = {"metadataEntries": [{"attribute": "collection_type", "value": "Project"}]}
        for k, metadict in parsed_data.items():
            for field, valueslist in metadict.items():
                if valueslist: # only add it user provided values
                    try:
                        val = valueslist[i]
                        if val == 'nan':
                            continue
                    except IndexError:
                        if field in singular_fields: # check for singular field
                            val = valueslist[0]
                        else: # User did not provided values for optional fields
                            continue
                    temp['metadataEntries'].append({'attribute': field, 'value': val})
            else:
                # Get dme field names for collection and write output to file
                poc, origin, nsamples, method, sdate = dict2list(parsed_data, ["project_poc", "origin", "number_of_cases", "method", "start_date"], i=i, override_index=["project_poc", "start_date"])
                poc = poc.replace(" ","")
                origin = origin.replace(" ","-")
                method = method.replace(" ","-")
                sdate = sdate.split()[0]

                collection_name = 'Project_{}_{}_{}{}_{}'.format(poc, origin, nsamples, method, sdate)

                if pid:
                    collection_name = 'Project_{}_{}_{}_{}{}_{}'.format(poc, origin, pid, nsamples, method, sdate)

                outfile = os.path.join(opath, '{}.metadata.json'.format(collection_name))
                path_exists(os.path.join(opath, '{}'.format(collection_name)))

                subcollections[collection_name] = outfile

                #Save upload collection metadata data as JSON file
                with open(outfile, 'w') as file:
                    json.dump(temp, file, sort_keys=True, indent=4)

    return subcollections


def _sample(parsed_data, template, opath, dme_vault, additional_metadata = {}):
    """Private helper function to generate(). Extracts Sample metadata from parsed_data,
    adds it to the template, and writes it to a new file. Returns a dictionary containing
    collection information where [keys] are collection_name and values are the output
    filename for parsed metadata. The relationship between each project request to
    rawdata sample collection(s) is '1:M'. Also merges additional metadata if provided,
    see tsv2dict() for generating the expected data structure.
    """
    subcollections = {}

    for sid, metadict in parsed_data.items():
            temp = {"metadataEntries": [{"attribute": "collection_type", "value": "Sample"}]}
            for field, userdata in metadict.items():
                if userdata and userdata != 'nan':
                    temp['metadataEntries'].append({'attribute': field, 'value': userdata})
            else:
                sname = parsed_data[sid]["sample_name"]
                # Add optional runtime metadata
                if additional_metadata:
                    try:
                        metarun = additional_metadata[sname]
                        temp['metadataEntries'].extend(metarun)
                    except KeyError:
                        pass # Edge-case: no runtime metadata for that sample
                collection_name = 'Sample_{}_{}'.format(sid, sname)

                outfile = os.path.join(opath, '{}.metadata.json'.format(collection_name))
                path_exists(os.path.join(opath, '{}'.format(collection_name)))

                subcollections[collection_name] = outfile

                #Save upload collection metadata data as JSON file
                with open(outfile, 'w') as file:
                    json.dump(temp, file, sort_keys=True, indent=4)

    return subcollections


def _analysis(parsed_data, template, opath, dme_vault):
    """Private helper function to generate(). Extracts Analysis metadata from parsed_data,
    adds it to the template, and writes it to a new file. Returns a dictionary containing
    collection information where [keys] are collection_name and values are the output
    filename for parsed metadata. The relationship between each project request to
    analysis collection is '1:1'; however, it is possible to have multiple analyses
    for a given project.
    """
    required = ['number_of_cases', 'method', 'assembly_name', 'gtf_ver', 'md5_all_inputs_serial']
    temp = {"metadataEntries": [{"attribute": "collection_type", "value": "Analysis"}]}
    subcollections = {}
    missing = []

    for field, userdata in parsed_data.items():
        temp['metadataEntries'].append({'attribute': field, 'value': userdata})

    # Check for required fields or dme attributes
    for dme_attr in required:
        try:
            require = parsed_data[dme_attr]
        except KeyError as e:
            missing.append(str(e))
    else:
        if missing:
            raise LookupError("""\n\nFatal: Failed to provide all required mandatory metadata for Analysis collection!
            Missing the following required DME attributes: {}
            Please update the provided analysis metadata file before running again!""".format(",".join(missing)))

    collection_name = 'Primary_Analysis_{}{}_{}_{}_{}'.format(parsed_data['number_of_cases'], parsed_data['method'], parsed_data['assembly_name'], parsed_data['gtf_ver'], parsed_data['md5_all_inputs_serial'])

    outfile = os.path.join(opath, '{}.metadata.json'.format(collection_name))
    path_exists(os.path.join(opath, '{}'.format(collection_name)))

    subcollections[collection_name] = outfile

    #Save upload collection metadata data as JSON file
    with open(outfile, 'w') as file:
        json.dump(temp, file, sort_keys=True, indent=4)

    return subcollections


def main():

    # @args(): Parses positional command-line args
    # @validate(): Checks if user inputs are vaild
    data_dict, project_dict, sample_dict, pid, metafile, analysisfile, convert, ipath, opath, vault = validate(args(sys.argv))

    # Output directory for collection and data-object metadata
    path_exists(opath)

    # Read in JSON files as dictionary
    data_dict = json2dict(data_dict)
    pi_dict, project_dict = separate(json2dict(project_dict), ["PI_Lab", "Project"])
    sample_dict = json2dict(sample_dict)

    # Convert optional metadata file from TSV to dictionary
    metarun = {}
    if metafile:
        metarun = mqc2dict(metafile)

    # Covert field from common name to dme_name
    if convert:
        pi_dict = field2DME(pi_dict, data_dict)
        project_dict = field2DME(project_dict, data_dict)
        sample_dict = field2DME(sample_dict, data_dict)

    # Get PATH to templates
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'data', 'templates')

    # Generate PI_Lab collection metadata
    pi_collects = generate(parsed_data=pi_dict, template=os.path.join(template_path, 'pi_lab_collection.json'), opath=opath, dme_vault=vault, helper=_pi)

    # Generate Project collection(s) metadata
    # Add MVD functionality later
    # Need Project key in spreadsheet to map to samples
    dme_prefix = os.path.join(opath, list(pi_collects.keys())[0])
    project_collects = generate(parsed_data=project_dict, template=os.path.join(template_path, 'project_collection.json'), opath=dme_prefix, dme_vault=vault, helper=_project, pid=pid)

    # Generate Sample collection(s) metadata
    dme_prefix = os.path.join(dme_prefix, list(project_collects.keys())[0])
    sample_collects = generate(parsed_data=sample_dict, template=os.path.join(template_path, 'sample_collection.json'), opath=dme_prefix, dme_vault=vault, helper=_sample, additional_metadata=metarun)

    # Generate Analysis collection metadata
    # If optional runtime metadata provided
    analysis_dict = {}
    if analysisfile:
        analysis_dict = tsv2dict(analysisfile)
        analysis_collects = generate(parsed_data=analysis_dict, template=os.path.join(template_path, 'analysis_collection.json'), opath=dme_prefix, dme_vault=vault, helper=_analysis)



if __name__ == '__main__':

    main()
