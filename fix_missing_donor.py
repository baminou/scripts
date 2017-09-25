#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is used to add the donor ID to the job json in an EGA-Collab transfer.
# The script has one file one file in argument (-i) that contains the absolute or relative
# path of the file (1st column), submitter id (2nd column), donor id (3rd column).

import json
import argparse

def main():
    """ Main program """
    parser = argparse.ArgumentParser(description='Fix EGA-Collab job json')
    parser.add_argument('-i', '--input', dest="input", help="File containg the list of job.json to fix", required=True)
    results = parser.parse_args()

    with open(results.input) as f:
        next(f)
        for line in f:
            print line
            json_file=line.strip('\n').split('\t')[0]
            submitter_id=line.strip('\n').split('\t')[1]
            donor_id=line.strip('\n').split('\t')[2]

            with open(json_file) as json_data:
                d = json.load(json_data)
		try:
                	print d['submitter_donor_id']
		except KeyError, err:
			d['submitter_donor_id'] = donor_id
		print json.dumps(d, indent=4, sort_keys=True)
		exit()

    return 0

if __name__ == "__main__":
    main()
