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

import daiquiri
import requests

from eml_2_1_1 import Eml

logger = daiquiri.getLogger('shchema_org: ' + __name__)
open_tag = '<script type="application/ld+json">\n'
close_tag = '\n</script>'

def dataset(pid: str, env: str=None):

    json_ld = {}
    json_ld['@context'] = "http://schema.org"
    json_ld['@type'] = "Dataset"

    _ = pid.split('.')
    pid_frag = f'{_[0]}/{_[1]}/{_[2]}'
    if env in ('d', 's'):
        dpath = f'https://pasta-{env}.lternet.edu/package'
    else:
        dpath = f'https://pasta.lternet.edu/package'
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
    html = f'{open_tag}{j}{close_tag}'

    return html

def main():
    return 0


if __name__ == "__main__":
    main()
