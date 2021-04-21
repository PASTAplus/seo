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

import daiquiri

import webapp.schema_org as schema_org

sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_schema_org: ' + __name__)


def test_dataset():
    json_ld = schema_org.dataset(pid='edi.3.1', env='p', raw='True')
    print('\n' + json_ld)
    assert json_ld is not None


def test_repository():
    json_ld = schema_org.repository(raw='True')
    print('\n' + json_ld)
    assert json_ld is not None
