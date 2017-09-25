#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
from icgconnect import collab
from icgconnect.utils import file_utils
import os

def main():
    parser = argparse.ArgumentParser(description='Fix EGA-Collab job json')
    parser.add_argument('-i', '--input', dest="input", help="File containg the list of job.json to fix", required=True)
    results = parser.parse_args()

    fix_file(results.input)

    return 0

def fix_file(input_file):
    with open(input_file) as json_data:
        d = json.load(json_data)
        try:
            print d.get('input')['file_size']
        except KeyError, err:
            object_id = d.get('input').get('object_id')
            file_name = d.get('input').get('file_name')
            tmp_file = os.path.join('/tmp',file_name)
            collab.download(object_id,'icgc-storage-client','/tmp')
            d['input']['file_size'] = str(file_utils.get_file_size(tmp_file))

            with open(input_file, 'w') as f:
                f.write(json.dumps(d, indent=4, sort_keys=True))
            file_utils.delete_file(tmp_file)


if __name__ == "__main__":
    main()