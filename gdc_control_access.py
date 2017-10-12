#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Add access and controlled attribute to json')
    parser.add_argument('-i', '--input', dest="input", help="File containg json", required=True)
    parser.add_argument('-o', '--output', dest="output", help="Output path", required=True)
    parser.add_argument('-t', '--type', dest="type", help="Type of file", required=True)
    results = parser.parse_args()

    data = {}

    with open(results.input) as json_data:
        data = json.load(json_data)

        project = None
        ssm_id = None

        if results.type == "gene_centric":
            data = get_gene_centric(data)

        elif results.type == "case_centric":
            data = get_case_centric(data)

        elif results.type == "ssm_centric":
            data = get_ssm_centric(data)

        elif results.type == "ssm_occurrence":
            data = get_ssm_occurrence(data)

    with open(results.output,'w') as fp:
        json.dump(data,fp)

    return 0

def get_gene_centric(data):
    for i in xrange(0,len(data.get('case'))):
        for y in xrange(0,len(data.get('case')[i].get('ssm'))):
            for z in xrange(0,len(data.get('case')[i].get('ssm')[y].get('observation'))):
                ssm_id = data.get('case')[i].get('ssm')[y].get('ssm_id')
                project = data.get('case')[i].get('project').get('project_id')
                data.get('case')[i].get('ssm')[y].get('observation')[z]['access'] = get_access(project,ssm_id)
                data.get('case')[i].get('ssm')[y].get('observation')[z]['project_id'] = project
    return data

def get_case_centric(data):
    for i in xrange(0,len(data.get('gene'))):
        for y in xrange(0,len(data.get('gene')[i].get('ssm'))):
            for z in xrange(0,len(data.get('gene')[i].get('ssm')[y].get('observation'))):
                ssm_id = data.get('gene')[i].get('ssm')[y]['ssm_id']
                project = data.get('project').get('project_id')
                data.get('gene')[i].get('ssm')[y].get('observation')[z]['access'] = get_access(project, ssm_id)
                data.get('gene')[i].get('ssm')[y].get('observation')[z]['project_id'] = project
    return data

def get_ssm_centric(data):
    ssm_id = data.get('ssm_id')
    for i in xrange(0,len(data.get('occurrence'))):
        for y in xrange(0,len(data.get('occurrence')[i].get('case'))):
            for z in xrange(0,len(data.get('occurrence')[i].get('case').get('observation'))):
                project = data.get('occurrence')[i].get('case').get('project').get('project_id')
                data.get('occurrence')[i].get('case').get('observation')[z]['access'] = get_access(project, ssm_id)
                data.get('occurrence')[i].get('case').get('observation')[z]['project_id'] = project
    return data

def get_ssm_occurrence(data):
    ssm_id = data.get('ssm').get('ssm_id')
    project = data.get('case').get('project').get('project_id')

    for i in xrange(0,len(data.get('case').get('observation'))):
        data.get('case').get('observation')[i]['access'] = get_access(project, ssm_id)
        data.get('case').get('observation')[i]['project_id'] = project

    return data


def get_access(project_name, ssm_id):
    if project_name in controlled_projects():
        if ssm_id[0].isdigit():
            return 'open'
        else:
            return 'control'
    elif project_name in forced_controlled_projects():
        return 'control'
    else:
        return 'open'


def controlled_projects():
    return ['TCGA-BRCA','TCGA-CHOL','TCGA-ACC','TCGA-KIRP','TCGA-GBM','TCGA-OV']

def forced_controlled_projects():
    return ['TCGA-LGG', 'TCGA-BLCA','TCGA-UCS']


if __name__ == "__main__":
    main()