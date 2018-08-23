#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_schema_org

:Synopsis:

:Author:
    servilla
  
:Created:
    8/16/18
"""
import os
import sys
import unittest

import daiquiri

import webapp.schema_org as schema_org

sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_schema_org: ' + __name__)


class TestSchemaOrg(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dataset(self):
        json_ld = schema_org.dataset(pid='edi.1.1', env='p', raw='True')
        print(json_ld)
        self.assertIsNotNone(json_ld)


if __name__ == '__main__':
    unittest.main()