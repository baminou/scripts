#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os
from overture_song.model import ApiConfig
from overture_song.client import Api, ManifestClient, StudyClient
from overture_song.tools import FileUploadClient
import subprocess
import requests

def main():
    parser = argparse.ArgumentParser(description='Generate a song payload using minimal arguments')
    parser.add_argument('-s', '--study-id', dest="study_id", help="Study ID", required=True)
    parser.add_argument('-u', '--server-url', dest="server_url", help="Server URL", required=True)
    parser.add_argument('-p', '--payload', dest="payload", help="JSON Payload", required=True)
    parser.add_argument('-t', '--access-token', dest="access_token", default=os.environ.get('ACCESSTOKEN',None),help="Server URL")
    results = parser.parse_args()

    study_id = results.study_id
    server_url = results.server_url
    access_token = results.access_token
    payload = results.payload

    config = ApiConfig(server_url,study_id,access_token, debug=True)
    api = Api(config)

    study_client = StudyClient(api)

    client = FileUploadClient(api, payload, is_async_validation=True,ignore_analysis_id_collisions=True)

    client.upload()
    client.update_status()
    api.save(client.upload_id, ignore_analysis_id_collisions=True)
    client.save()

    manifest_filename = client.analysis_id+'.manifest.txt'
    manifest_client = ManifestClient(api)
    manifest_client.create_manifest(client.analysis_id,os.path.join(os.getcwd(),manifest_filename))

    subprocess.check_output(['icgc-storage-client','upload','--manifest',os.path.join(os.getcwd(),manifest_filename)])

    #client.publish()


if __name__ == "__main__":
    main()
