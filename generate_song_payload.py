#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from icgconnect.utils.file_utils import get_file_md5, get_file_size, get_file_type
from icgconnect import icgc
import os

def main():
    parser = argparse.ArgumentParser(description='Generate a song payload using minimal arguments')
    parser.add_argument('-d', '--donor-id', dest="donor_id", help="Donor ID", required=True)
    parser.add_argument('-i', '--insert-size', dest="insert_size", help="Experiment Insert Size")
    parser.add_argument('-a', '--analysis-id', dest="analysis_id", help="Analysis ID")
    parser.add_argument('-st', '--sample-type', dest="sample_type", help="Sample type", required=True)
    parser.add_argument('-at', '--analysis-type', dest="analysis_type", help="Analysis type", required=True)
    parser.add_argument('-l', '--library-strategy', dest="library_strategy", help="Library Strategy", required=True)
    parser.add_argument('-o', '--output', dest="output", help="Output file", required=True)
    parser.add_argument('--paired-end', dest="paired_end", help="Experiment is paired end", action='store_true')
    parser.add_argument('--single-end', dest="paired_end", help="Experiment is single end", action='store_false')
    parser.add_argument('-f', '--files', dest="files", nargs='+', help="Path of files to add to the payload", required=True)
    results = parser.parse_args()

    for _file in results.files:
        if not os.path.isfile(_file):
            print "File: "+_file+"  does not exist"
            exit(1)

    files = []
    for _file in results.files:
        files.append(get_file_info(_file))

    json_payload = {}
    json_payload['analysisId'] = results.analysis_id
    json_payload['analysisType'] = results.analysis_type

    json_payload['experiment'] = {}
    json_payload['experiment']['insertSize'] = results.insert_size
    json_payload['experiment']['libraryStrategy'] = results.library_strategy
    json_payload['experiment']['pairedEnd'] = results.paired_end

    json_payload['sample'] = []
    json_payload['sample'].append({})
    json_payload['sample'][0]['sampleSubmitterId'] = icgc.get_sample_submitter_id_from_donor_id(results.donor_id)
    json_payload['sample'][0]['donor'] = get_donor_info(results.donor_id)
    json_payload['sample'][0]['specimen'] = get_specimen_info(results.donor_id)
    json_payload['sample'][0]['sampleType'] = results.sample_type
    json_payload['file'] = files

    with open(results.output,'w') as f:
        json.dump(json_payload,f,indent=4,sort_keys=True)




def get_specimen_info(donor_id):
    return {
        'specimenClass': icgc.get_specimen_class_from_donor_id(donor_id),
        'specimenType': icgc.get_specimen_type_from_donor_id(donor_id),
        'specimenSubmitterId': icgc.get_submitted_specimen_id_from_donor_id(donor_id),
    }

def get_donor_info(donor_id):
    return {
        'donorGender': icgc.get_gender_from_donor_id(donor_id),
        'donorSubmitterId': icgc.get_submitter_donor_id_from_donor_id(donor_id)
    }

def get_file_info(fname):
    return {
            'fileName': os.path.basename(fname),
            'fileMd5sum': get_file_md5(fname),
            'fileSize': get_file_size(fname),
            'fileType': get_file_type(fname).upper()
        }

if __name__ == "__main__":
    main()
