#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

def main():
    """ Main program """
    parser = argparse.ArgumentParser(description='Fix EGA-Collab job json')
    parser.add_argument('-i', '--input', dest="input", help="File containg the list of job.json to fix", required=True)
    results = parser.parse_args()

    with open(results.input,'r') as f:
        f.readline()
        for line in f:
            with open(line.split('\t')[0],'r') as json_data:
                d = json.load(json_data)
                project_code=d.get('project_code')
                files_array=d.get('files')
                for _file in files_array:
                    print 'data/'+project_code+'/'+_file['ega_file_id']+'.aes'
                    print 'data/'+project_code+'/'+_file['ega_file_id']+'.aes.md5'
                #print ['data/'+project_code+'/'+x['ega_file_id']+'.aes' for x in files_array]

    return 0

if __name__ == "__main__":
    main()
