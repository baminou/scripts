#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import logging

def main():
    parser = argparse.ArgumentParser(description='Fix EGA-Collab job json')
    parser.add_argument('-i', '--input', dest="input", help="File containg the list of job.json to fix", required=True)
    parser.add_argument('-o', '--output', dest="output", help="File containg the list of job.json to fix", required=True)
    results = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    for dir in list_job_dirs(results.input):
        logger.info('Transfering '+dir)
        project_name = dir.split('.')[2]

        try:
            os.mkdir(os.path.join(results.output, project_name))
            create_jtracker_structure(os.path.join(results.output,project_name))
        except OSError, err:
            logger.warning(str(err))

        try:
            shutil.copytree(os.path.join(results.input,dir), os.path.join(results.output,project_name,dir))
        except OSError, err:
            logger.warning(str(err))

        logger.info(dir+' transferred')

    return 0


def list_job_dirs(path):
    dirs = []
    for folder in os.listdir(path):
        if folder.startswith('job.') and os.path.isdir(os.path.join(path,folder)):
            dirs.append(folder)
    return dirs

def create_jtracker_structure(path):
    os.mkdir(os.path.join(path,'job_stacte.backlog'))
    os.mkdir(os.path.join(path,'job_stacte.completed'))
    os.mkdir(os.path.join(path,'job_stacte.failed'))
    os.mkdir(os.path.join(path,'job_stacte.running'))
    os.mkdir(os.path.join(path,'job_stacte.queued'))


if __name__ == "__main__":
    main()