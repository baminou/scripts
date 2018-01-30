#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import urllib
from icgconnect.icgc import get_donor_id_from_submitted_donor_id, get_donor

#Example input job:
# https://github.com/ICGC-TCGA-PanCancer/oxog-ops/blob/master/oxog-collab-jobs/completed-jobs/BOCA-UK.CGP_donor_1397077.json

# The OxoQC file can be found
# https://dcc.icgc.org/api/v1/download?fn=/PCAWG/quality_control_info/oxoQ_table_2943_2016-04-20.txt

def main():
    parser = argparse.ArgumentParser(description='A job json file from oxojo transfer')
    parser.add_argument('-i', '--input', dest="input", help="File containg json")
    parser.add_argument('-d', '--dir', dest="directory", help="Directory containg jsons")
    parser.add_argument('-snv', '--snv-padding', dest="snv", help="SNV padding", required=True)
    parser.add_argument('-sv', '--sv-padding', dest="sv", help="SV padding", required=True)
    parser.add_argument('-indel', '--indel-padding', dest="indel", help="Indel padding", required=True)
    parser.add_argument('-o','--out-dir',dest="out_dir", help="Output directory")
    results = parser.parse_args()


    if results.input is None and results.directory is None:
        parser.error('-i or -d is required for file or directory respectively')

    if not results.input is None and not results.directory is None:
        parser.error('Choose between -i or -d for file or directory respectively')

    if not results.directory is None and results.out_dir is None:
        parser.error('Please enter an output directory -o')

    if not results.out_dir is None:
        if not os.path.isdir(results.out_dir):
            print results.out_dir+" does not exist"
            exit(1)

    oxoq_scores = download_oxoq_file()

    if not results.input is None:
        create_job_json(results.input, results.snv, results.sv, results.indel)

    if not results.directory is None:
        for _file in os.listdir(results.directory):
            if _file.endswith('.json'):
                print os.path.join(results.directory,_file)
                try:
                    create_job_json(os.path.join(results.directory,_file),results.snv,results.sv,results.indel, results.out_dir)
                except IndexError, err:
                    print str(err)


def create_job_json(oxog_job_file, snv, sv, indel,out_dir=None):
    if not os.path.isfile(oxog_job_file):
        raise ValueError("File "+oxog_job_file+" does not exist")

    json_data = json.load(open(oxog_job_file))

    job_json = {}
    job_json['associated_vcfs'] = get_associated_vcfs(json_data)
    job_json['normal_bam'] = get_normal_bam(json_data)
    job_json['tumour_bams'] = get_tumor_bams(json_data)
    job_json['snv_padding'] = int(snv)
    job_json['sv_padding'] = int(sv)
    job_json['indel_padding'] = int(indel)
    job_json['aliquot_id'] = json_data.get('tumors')[0].get('aliquot_id')

    job_json['donor_id'] = get_donor_id_from_submitted_donor_id(json_data.get('project_code'),json_data.get('submitter_donor_id'))

    sample = download_pcawg_samples()[job_json.get('donor')['submitter_id']]
    job_json['sample_submitter_id'] = sample['icgc_sample_id']
    job_json['experiment_library_strategy'] = sample['library_strategy']

    if not out_dir == None:
        with open(os.path.join(out_dir,'job.'+os.path.basename(oxog_job_file)),'w') as f:
            json.dump(job_json,f, indent=4, sort_keys=True)
        return

    print json.dumps(job_json,indent=4,sort_keys=True)


def download_oxoq_file():
    _oxo_scores = {}
    oxo_filename = "oxoQ_table_2943_2016-04-20.txt"
    urllib.urlretrieve('https://dcc.icgc.org/api/v1/download?fn=/PCAWG/quality_control_info/'+oxo_filename,os.path.join('/tmp',oxo_filename))

    with open(os.path.join('/tmp',oxo_filename)) as f:
        f.readline()
        for _line in f.readlines():
            _oxo_scores[_line.split('\t')[0]] = _line.split('\t')[1].strip('\n')

    os.remove(os.path.join('/tmp',oxo_filename))
    return _oxo_scores


def download_pcawg_samples():
    samples = {}
    filename = 'pcawg_sample_sheet.tsv'
    urllib.urlretrieve('http://pancancer.info/data_releases/latest/'+filename,os.path.join('/tmp',filename))
    with open(os.path.join('/tmp',filename)) as f:
        f.readline()
        for _line in f.readlines():
            sample = _line.strip('\n').split('\t')
            samples[sample[2]] = {'icgc_donor':sample[3],'submitter_specimen_id':sample[6],'icgc_specimen_id':sample[7],'icgc_sample_id':sample[8],
                                  'icgc_sample_id': sample[9],'dcc_specimen_type':sample[10],'library_strategy':sample[11]}
    os.remove(os.path.join('/tmp', filename))
    return samples


def get_normal_bam(json_data):
    normal_json = filter_json_object_list_by_extension(json_data.get('normal').get('files'),'file_name','.bam')[0]
    normal_json['minibam'] = {}
    normal_json['minibam']['bam_file_name'] = normal_json['file_md5sum']+'.mini.bam'
    normal_json['minibam']['bai_file_name'] = normal_json['file_md5sum']+'.mini.bam.bai'

    normal_json['specimen'] = {}
    normal_json['specimen']['type'] = json_data.get('normal').get('specimen_type')
    normal_json['specimen']['submitter_id'] = json_data.get('normal').get('submitter_id')
    return normal_json

def get_tumor_bams(json_data):
    tumors = []
    for i in xrange(0,len(json_data.get('tumors'))):
        tumor_json = filter_json_object_list_by_extension(json_data.get('tumors')[i].get('files'),'file_name','.bam')[0]
        tumor_json['oxog_score'] = float(json_data.get('tumors')[i].get('oxog_score'))
        tumor_json['minibam'] = {}
        tumor_json['minibam']['bam_file_name'] = tumor_json['file_md5sum']+".mini.bam"
        tumor_json['minibam']['bai_file_name'] = tumor_json['file_md5sum']+".mini.bam.bai"

        tumor_json['specimen'] = {}
        tumor_json['specimen']['submitter_id'] = json_data.get('tumors')[i].get('submitter_specimen_id')
        tumor_json['specimen']['type'] = json_data.get('tumors')[i].get('data_type')

        tumors.append(tumor_json)
    return tumors


def get_associated_vcfs(json_data):
    vcf_files = []
    for source in ["broad","dkfz_embl","muse","sanger"]:
        vcf_files = vcf_files + filter_json_object_list_by_extension(json_data.get(source).get('files'),'file_name','.vcf.gz')
    return filter_json_object_list_by_substring(vcf_files, 'file_name', 'somatic')

def filter_json_object_list_by_extension(_list, _key,_ext):
    new_list = []
    for _elem in _list:
        if _elem.get(_key).endswith(_ext):
            new_list.append(_elem)
    return new_list

def filter_json_object_list_by_substring(_list, _key, _subs):
    new_list = []
    for _elem in _list:
        if _subs in _elem.get(_key):
            new_list.append(_elem)
    return new_list

if __name__ == "__main__":
    main()