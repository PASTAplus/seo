#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_sitemaps_org

:Synopsis:

:Author:
    servilla
  
:Created:
    8/24/18
"""
import os
import sys

import daiquiri

from webapp.config import Config
import webapp.sitemaps_org as sitemaps_org


sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_sitemaps_org: ' + __name__)


def test_generate_sitemap():
    pids = ['knb-lter-nin.1.1']
    portal = Config.PORTAL_P
    sitemap = sitemaps_org.generate_sitemap(pids=pids, portal=portal)
    assert isinstance(sitemap, str)


def test_get_count():
    count = sitemaps_org.get_count(pasta=Config.PASTA_P)
    assert count > 0


def test_get_pids():
    pids = sitemaps_org.get_pids(env=Config.PASTA_P)
    assert pids is not None
