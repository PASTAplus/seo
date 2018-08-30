#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: sitemaps_org

:Synopsis:

:Author:
    servilla

:Created:
    8/24/18
"""
import tarfile

import daiquiri
from lxml import etree
import requests

from webapp.config import Config
import webapp.utility as utility


logger = daiquiri.getLogger('sitemaps_org: ' + __name__)


def generate_sitemap(pids: list, portal: str) -> str:

    nsmap = {None: 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urlset = etree.Element('urlset', nsmap=nsmap)

    for pid in pids:
        scope, identifier, revision = utility.pid_triple(pid=pid)
        location = f'{portal}/mapbrowse?scope={scope}&' + \
                   f'identifier={identifier}&revision={revision}'
        url = etree.Element('url')
        loc = etree.SubElement(url, 'loc')
        loc.text = location
        urlset.append(url)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                  etree.tostring(urlset, pretty_print=True).decode('utf-8')

    return xml


def generate_sitemap_bundle(env: str = None,
                            page_size: int = Config.SITEMAP_PAGE_SIZE):
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

    package_count = get_count(pasta=pasta)
    if package_count % page_size > 0:
        pages = (package_count // page_size) + 1
    else:
        pages = (package_count // page_size)

    pids = get_pids(env=pasta, start=0, rows=package_count)

    # Generate page-sized sitemaps
    sitemaps = list()
    start = 0
    for page in range(pages):
        sitemap = generate_sitemap(pids[start:start + page_size], portal)
        fn = f'sitemap{page}.xml'
        sitemaps.append(fn)
        start = start + page_size
        with open(f'{cache}/{fn}', 'w') as fp:
            fp.write(sitemap)

    # Generate sitemap_index.xml
    sitemap_index_xml = generate_sitemap_index(portal.replace('/nis', ''), pages)
    with open(f'{cache}/sitemap_index.xml', 'w') as fp:
        fp.write(sitemap_index_xml)

    sitemap_bundle = f'{cache}/sitemap.tar.gz'
    with tarfile.open(sitemap_bundle, 'w:gz') as tar:
        tar.add(f'{cache}/sitemap_index.xml', arcname='sitemap_index.xml')
        for sitemap in sitemaps:
            tar.add(f'{cache}/{sitemap}', arcname=sitemap)

    return sitemap_bundle


def generate_sitemap_index(portal: str, pages: int)-> str:
    nsmap = {None: 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemapindex = etree.Element('sitemapindex', nsmap=nsmap)
    for page in range(pages):
        sitemap = etree.Element('sitemap')
        loc = etree.SubElement(sitemap, 'loc')
        loc.text = f'{portal}/sitemap{page}.xml'
        sitemapindex.append(sitemap)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                etree.tostring(sitemapindex, pretty_print=True).decode('utf-8')
    return xml


def get_count(pasta: str=Config.PASTA_P) -> int:
    solr_url = f'{pasta}/search/eml?defType=edismax&q=*&fl=packageid&' + \
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
    # sitemap = generate_sitemap(env='p')
    # with open(f'{Config.CACHE_P}/sitemap.xml', 'w') as fp:
    #     fp.write(sitemap)
    #
    # sitemap = generate_sitemap(env='s')
    # with open(f'{Config.CACHE_S}/sitemap.xml', 'w') as fp:
    #     fp.write(sitemap)
    #
    # sitemap = generate_sitemap(env='d')
    # with open(f'{Config.CACHE_D}/sitemap.xml', 'w') as fp:
    #     fp.write(sitemap)

    generate_sitemap_bundle()

    return 0


if __name__ == "__main__":
    main()
