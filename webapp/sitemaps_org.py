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


def generate_sitemap(env: str=None) -> str:
    if env in ('d', 'dev', 'development'):
        pasta = Config.PASTA_D
        portal = Config.PORTAL_D
        cache = Config.CACHE_D
    elif env in ('s', 'stage', 'staging'):
        pasta = Config.PASTA_S
        portal = Config.PORTAL_S
        cache = Config.CACHE_S
    else:
        pasta = Config.PASTA_P
        portal = Config.PORTAL_P
        cache = Config.CACHE_P

    nsmap = {None: 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urlset = etree.Element('urlset', nsmap=nsmap)
    sitemap = etree.ElementTree(urlset)

    count = get_count(env=pasta)
    pids = get_pids(env=pasta, start=0, rows=count)
    for pid in pids:
        scope, identifier, revision = utility.pid_triple(pid=pid)
        location = f'{portal}/mapbrowse?scope={scope}&' + \
                   f'identifier={identifier}&revision={revision}'
        url = etree.Element('url')
        loc = etree.SubElement(url, 'loc')
        loc.text = location
        urlset.append(url)

    sitemap_xml = etree.tostring(sitemap, pretty_print=True).decode('utf-8')

    return sitemap_xml


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
    sitemap = generate_sitemap(env='p')
    with open(f'{Config.CACHE_P}/sitemap.xml', 'w') as fp:
        fp.write(sitemap)

    sitemap = generate_sitemap(env='s')
    with open(f'{Config.CACHE_S}/sitemap.xml', 'w') as fp:
        fp.write(sitemap)

    sitemap = generate_sitemap(env='d')
    with open(f'{Config.CACHE_D}/sitemap.xml', 'w') as fp:
        fp.write(sitemap)

    return 0


if __name__ == "__main__":
    main()
