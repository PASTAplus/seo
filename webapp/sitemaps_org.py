#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: sitemaps_org

:Synopsis:

:Author:
    servilla

:Created:
    8/24/18
"""
import daiquiri
from lxml import etree
import requests

from webapp.config import Config


logger = daiquiri.getLogger('sitemaps_org: ' + __name__)


def get_count(env: str=Config.PASTA_P) -> int:
    solr_url = f'{env}/search/eml?defType=edismax&q=*&fl=packageid&' + \
               f'sort=score,desc&sort=packageid,asc&debug=false&' + \
               f'start=0&rows=0'

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        result_set = r.text.encode('utf-8')
    else:
        raise requests.exceptions.ConnectionError()

    root = etree.fromstring(result_set)
    return int(root.get('numFound'))


def get_pids(env: str=Config.PASTA_P, start: str=0, rows: str=Config.ROWS):
    solr_url = f'{env}/search/eml?defType=edismax&q=*&fl=packageid&' + \
               f'sort=score,desc&sort=packageid,asc&debug=false&' + \
               f'start={start}&rows={rows}'

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        result_set = r.text.encode('utf-8')
    else:
        raise requests.exceptions.ConnectionError()

    root = etree.fromstring(result_set)
    _ = root.findall('.//packageid')
    pids = list()
    for pid in _:
        pids.append(pid.text)

    return pids


def main():
    return 0


if __name__ == "__main__":
    main()
