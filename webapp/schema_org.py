#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: shchema_org

:Synopsis:

:Author:
    servilla

:Created:
    8/16/18
"""
import json
import os.path

import requests

from webapp.config import Config
from webapp.eml_2_1_1 import Eml

open_tag = '<script type="application/ld+json">\n'
close_tag = '\n</script>'


def dataset(pid: str, env: str=None, raw: str=None):

    json_ld = dict()
    json_ld['@context'] = "http://schema.org"
    json_ld['@type'] = "Dataset"

    if env in ('d', 'dev', 'development'):
        dpath = Config.PASTA_D
        cache = Config.CACHE_D
    elif env in ('s', 'stage', 'staging'):
        dpath = Config.PASTA_S
        cache = Config.CACHE_S
    else:
        dpath = Config.PASTA_P
        cache = Config.CACHE_P


    file_path = f'{cache}{pid}.json'

    if os.path.isfile(file_path):
        # Read from cached location
        with open(file_path, 'r') as fp:
            j = fp.read()
    else:
        # Read from PASTA web service
        _ = pid.split('.')
        pid_frag = f'{_[0]}/{_[1]}/{_[2]}'
        pasta_uri = f'{dpath}/metadata/eml/{pid_frag}'

        r = requests.get(pasta_uri)
        if r.status_code == requests.codes.ok:
            eml = r.text
        else:
            raise requests.exceptions.ConnectionError()

        eml = Eml(eml=eml)
        name = eml.title
        description = eml.abstract

        json_ld['name'] = name
        json_ld['description'] = description
        j = json.dumps(json_ld, indent=2)
        with open(file_path, 'w') as fp:
            fp.write(j)

    if raw in ('t', 'T', 'true', 'True'):
        response = j
    else:
        response = f'{open_tag}{j}{close_tag}'

    return response


def main():
    return 0


if __name__ == "__main__":
    main()
