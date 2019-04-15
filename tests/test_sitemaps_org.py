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
import unittest

import daiquiri

from webapp.config import Config
import webapp.sitemaps_org as sitemaps_org


sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_sitemaps_org: ' + __name__)


class TestSitemapsOrg(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_sitemap(self):
        pids = ['knb-lter-nin.1.1']
        portal = Config.PORTAL_P
        sitemap = sitemaps_org.generate_sitemap(pids=pids, portal=portal)
        self.assertIsInstance(sitemap, str)

    def test_get_count(self):
        count = sitemaps_org.get_count(pasta=Config.PASTA_P)
        self.assertGreater(count, 0)

    def test_get_pids(self):
        pids = sitemaps_org.get_pids(env=Config.PASTA_P)
        self.assertIsNotNone(pids)

if __name__ == '__main__':
    unittest.main()