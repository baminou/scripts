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

        elif results.type == "ssm_occurrence_centric":
            data = get_ssm_occurrence(data)

    with open(results.output,'w') as fp:
        json.dump(data,fp)

    return 0

def get_gene_centric(data):
    for i in xrange(0,len(data.get('case'))):
        primary_site = [data.get('case')[i].get('project').get('primary_site')]
        disease_type = [data.get('case')[i].get('project').get('disease_type')]
        project_name = data.get('case')[i].get('project').get('project_id')

        primary_site = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['primary_site']
        disease_type = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['disease_type']

        data.get('case')[i].get('project')['primary_site'] = primary_site
        data.get('case')[i].get('project')['disease_type'] = disease_type

        for y in xrange(0,len(data.get('case')[i].get('ssm'))):
            for z in xrange(0,len(data.get('case')[i].get('ssm')[y].get('observation'))):
                ssm_id = data.get('case')[i].get('ssm')[y].get('ssm_id')
                project = data.get('case')[i].get('project').get('project_id')
                data.get('case')[i].get('ssm')[y].get('observation')[z]['access'] = get_access(project,ssm_id)
                data.get('case')[i].get('ssm')[y].get('observation')[z]['project_id'] = project
    return data

def get_case_centric(data):
    primary_site = [data.get('project').get('primary_site')]
    disease_type = [data.get('project').get('disease_type')]
    project_name = data.get('project').get('project_id')

    primary_site = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['primary_site']
    disease_type = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['disease_type']

    data.get('project')['primary_site'] = primary_site
    data.get('project')['disease_type'] = disease_type

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
        primary_site = [data.get('occurrence')[i].get('case').get('project').get('primary_site')]
        disease_type = [data.get('occurrence')[i].get('case').get('project').get('disease_type')]
        project_name = data.get('occurrence')[i].get('case').get('project').get('project_id')

        primary_site = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['primary_site']
        disease_type = adjust_primary_site_and_disease(primary_site, disease_type, project_name)['disease_type']

        data.get('occurrence')[i].get('case').get('project')['primary_site'] = primary_site
        data.get('occurrence')[i].get('case').get('project')['disease_type'] = disease_type

        for z in xrange(0,len(data.get('occurrence')[i].get('case').get('observation'))):
            project = data.get('occurrence')[i].get('case').get('project').get('project_id')
            data.get('occurrence')[i].get('case').get('observation')[z]['access'] = get_access(project, ssm_id)
            data.get('occurrence')[i].get('case').get('observation')[z]['project_id'] = project
    return data

def get_ssm_occurrence(data):
    ssm_id = data.get('ssm').get('ssm_id')
    project = data.get('case').get('project').get('project_id')

    primary_site = [data.get('case').get('project').get('primary_site')]
    disease_type = [data.get('case').get('project').get('disease_type')]

    primary_site = adjust_primary_site_and_disease(primary_site, disease_type, project)['primary_site']
    disease_type = adjust_primary_site_and_disease(primary_site, disease_type, project)['disease_type']

    data.get('case').get('project')['primary_site'] = primary_site
    data.get('case').get('project')['disease_type'] = disease_type

    for i in xrange(0,len(data.get('case').get('observation'))):
        data.get('case').get('observation')[i]['access'] = get_access(project, ssm_id)
        data.get('case').get('observation')[i]['project_id'] = project

    return data

def get_specific_projects():
    return ['TCGA-LUSC','TARGET-NBL','TCGA-GBM','TCGA-UVM']

def adjust_primary_site_and_disease(original_primary_site, original_disease_type, project_name):
    primary_site = original_primary_site
    disease_type = original_disease_type

    if project_name == 'TCGA-LUSC':
        primary_site = ['Bronchus', 'Lung']
        disease_type = ['Squamous Cell Neoplasms']
    elif project_name == 'TARGET-NBL':
        primary_site = ['Peripheral Nerves','Autonomic Nervous System']
        disease_type = ['Neuroepitheliomatous Neoplasms']
    elif project_name == 'TCGA-GBM':
        primary_site = ['Spinal Cord','Cranial Nerves','Other Parts Of Central Nervous System']
        disease_type = ['Glioblastoma Multiforme']
    elif project_name == 'TCGA-UVM':
        primary_site = ['Eye','Cranial Nerves','Adnexa']
        disease_type = ['Uveal Melanoma']

    return {'primary_site':primary_site, 'disease_type':disease_type}


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