#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
from lxml import etree
import json
from icgconnect.utils import file_utils
from icgconnect import collab
import logging

def main():
    parser = argparse.ArgumentParser(description='Fix EGA-Collab job json')
    parser.add_argument('-i', '--input', dest="input", help="File containg the list of job.json to fix", required=True)
    parser.add_argument('-t', '--token', dest="token", help="File containg the list of job.json to fix", required=True)
    parser.add_argument('-o', '--output', dest="output", help="File containg the list of job.json to fix", required=True)
    results = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    flag = 0

    try:
        project_code        = get_project_code(results.input)
    except lxml.etree.XMLSyntaxError, err:
        logger.error(results.input+' - '+str(err))
        flag = 1

    try:
        gnos_id             = get_gnos_id(results.input)
    except lxml.etree.XMLSyntaxError, err:
        logger.error(results.input+' - '+str(err))
        flag = 1

    try:
        submitter_donor_id  = get_submitter_donor_id(results.input)
    except lxml.etree.XMLSyntaxError, err:
        logger.error(results.input+' - '+str(err))
        flag = 1

    if flag == 1:
        logger.info(results.input+' is not valid. Program ends')
        exit(1)

    data_type           = 'WGS-BWA-miniBAM'
    job_filename        = 'job.'+gnos_id+'.'+project_code+'.'+submitter_donor_id+'.'+data_type+'.json'

    if os.path.isfile(os.path.join(results.output, job_filename)):
        return 0

    with open(os.path.join(results.output, job_filename), 'w') as outfile:
        json.dump({
            'gnos_id'               : gnos_id,
            'project_code'          : project_code,
            'submitter_donor_id'    : submitter_donor_id,
            'gnos_repo'             : "https://gtrepo-osdc-tcga.annailabs.com/",
            'aliquot_id'            : get_aliquot_id(results.input),
            'data_type'             : data_type,
            'files'                 : get_files(results.input, results.token, gnos_id, project_code)
        }, outfile,sort_keys=True, indent=4)

    return 0

def get_gnos_id(xml_file):
    with open(xml_file, 'r') as f:
        root = etree.XML(f.read())
        return root.findall("./Result/analysis_id")[0].text

def get_project_code(xml_file):
    return get_attribute(xml_file, 'dcc_project_code')

def get_attribute(xml_file, attribute_tag):
    with open(xml_file, 'r') as f:
        root = etree.XML(f.read())
        for attribute in root.findall("./Result/analysis_xml/ANALYSIS_SET/ANALYSIS/ANALYSIS_ATTRIBUTES/ANALYSIS_ATTRIBUTE"):
            if attribute.findall("TAG")[0].text == attribute_tag:
                return attribute.findall("VALUE")[0].text

def get_submitter_donor_id(xml_file):
    return get_attribute(xml_file, 'submitter_donor_id')

def get_aliquot_id(xml_file):
    with open(xml_file, 'r') as f:
        root = etree.XML(f.read())
        return root.findall("./Result/aliquot_id")[0].text

def get_files(xml_file, service_token, gnos_id, project_code,append_current_file=True):
    _files = []
    with open(xml_file, 'r') as f:
        root = etree.XML(f.read())
        for _file in root.findall("./Result/files/file"):
            object_id = collab.filename_get_post(gnos_id, service_token, _file.findall('filename')[0].text, project_code)['id']
            _files = _append_file_info_to_dict(_files,
                                      _file.findall('filename')[0].text,
                                      _file.findall('filesize')[0].text,
                                      _file.findall('checksum')[0].text,
                                               object_id)
    if append_current_file:
        object_id = collab.filename_get_post(gnos_id, service_token, xml_file, project_code)['id']
        _files = append_current_file_to_dict(xml_file, _files,object_id)
    return _files

def append_current_file_to_dict(xml_file_name, array_of_dict, object_id):
    array_of_dict = _append_file_info_to_dict(array_of_dict,
                              xml_file_name,
                              file_utils.get_file_size(xml_file_name),
                                  file_utils.get_file_md5(xml_file_name),
                                              object_id)
    return array_of_dict

def _append_file_info_to_dict(dict_array, file_name, file_size, file_md5sum, object_id=None):
    dict_array.append({
        'file_name'     : os.path.basename(file_name),
        'file_size'     : int(file_size),
        'file_md5sum'   : file_md5sum,
        'object_id'     : object_id
    })
    return  dict_array

def list_project_dirs(path):
    dirs = []
    for _dir in os.listdir(path):
        if _dir.startswith('project'):
            dirs.append(os.path.join(path,_dir))
    return dirs

def list_xml_files(path):
    files = []
    for _file in os.listdir(path):
        if _file.endswith('.xml'):
            files.append(os.path.join(path,_file))
    return files


if __name__ == "__main__":
    main()