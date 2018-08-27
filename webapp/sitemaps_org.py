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
import webapp.utility as utility


logger = daiquiri.getLogger('sitemaps_org: ' + __name__)


def generate_sitemap(env: str=Config.PASTA_P) -> str:
    if env == Config.PASTA_D:
        portal = Config.PORTAL_D
    elif env == Config.PASTA_S:
        portal = Config.PORTAL_S
    else:
        portal = Config.PORTAL_P

    nsmap = {None: 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urlset = etree.Element('urlset', nsmap=nsmap)
    sitemap = etree.ElementTree(urlset)

    count = get_count(env=env)
    pids = get_pids(env=env, start=0, rows=count)
    for pid in pids:
        scope, identifier, revision = utility.pid_triple(pid=pid)
        location = f'{portal}/mapbrowse?scope={scope}&' + \
                   f'identifier={identifier}&revision={revision}'
        url = etree.Element('url')
        loc = etree.SubElement(url, 'loc')
        loc.text = location
        urlset.append(url)

    return etree.tostring(sitemap)


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


def get_pids(env: str=Config.PASTA_P, start: int=0, rows: int=Config.ROWS):
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
