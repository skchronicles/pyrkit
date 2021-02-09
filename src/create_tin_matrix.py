#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import sys, pandas, os


def create(file, tin_dict, key_index=0, parse_index=4):
	"""Populates the TIN nested dictionary
	@param file <str>: Path to RSEQC output file with TIN values to extract
	@param tin_dict <dict>: Dictionary to populate where [samplebasename][transcriptid] = tin_value
	@param key_index <int>: Index of the field to join multiple files
	@param parse_index <int>: Index of field of interest (i.e. TIN value)
	"""

	with open(file, 'r') as fh:
		header = next(fh).strip().split('\t')
		colid = header[key_index]
		file = os.path.basename(file) # Remove PATH
		sample = file.split(".p2.Aligned.")[0]

		for line in fh:
			linelist = line.strip().split('\t')
			tid = linelist[key_index]
			tinvalue = linelist[parse_index]
			if sample not in tin_dict:
				tin_dict[sample] = {}

			tin_dict[sample][tid] = tinvalue

	return colid, tin_dict




if __name__ == '__main__':

	# Get filenames to parse
	args = sys.argv
	files = sys.argv[1:-1]
	opath = sys.argv[-1]

	if not os.path.isdir(opath):
		try:
			os.makedirs(opath)
		except OSError as e:
			print("Error: Failed to create output directory: {}\n{e}".format(opath, e), file=sys.stderr)
			sys.exit(1)

	# Check if at least two files were provided
	if not len(args) >= 3:
		print("FATAL: Failed to provide more than one input file!")
		sys.exit("Usage:\n python {} *.tin.xls outdir".format(args[0]))

	# Populate tins with TINS values for all transcripts across all samples
	tins = {}
	for file in files:
		keycolname, tins = create(file, tins)

	# Save tins as a tsv file: combined_TIN.tsv
	df = pandas.DataFrame(tins)
	df.to_csv(os.path.join(opath, "combined_TIN.tsv"), sep="\t", header=True, index=True, index_label = keycolname)
