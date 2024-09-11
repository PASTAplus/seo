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
import tempfile

import daiquiri

from lxml import etree

import webapp.schema_org as schema_org
from webapp.schema_org import convert_eml_to_schema_org

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


def test_default_encoding_format():
    """The default encodingFormat for unrecognized MIME types is
    'application/octet-stream'"""
    # Check that unrecognized file extensions result in the default
    # encodingFormat
    eml = etree.parse('tests/data/edi.3.1.xml')
    physical = eml.find('.//physical')
    physical.find('.//objectName').text = 'file.unknownextension'
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = tmpdir + "/edi.3.1.xml"
        eml.write(filename)
        json_ld = convert_eml_to_schema_org(
            file_path=filename,
            pid='edi.3.1',
            doi='https://doi.org/10.6073/pasta/bf143fa962e1edb822847bc0ee90c2f7'
        )
        assert '"encodingFormat": "application/octet-stream"' in json_ld
        assert '"encodingFormat": "text/csv"' not in json_ld

    # Check that recognized file extensions don't result in the default
    # encodingFormat
    eml = etree.parse('tests/data/edi.3.1.xml')
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = tmpdir + "/edi.3.1.xml"
        eml.write(filename)
        json_ld = convert_eml_to_schema_org(
            file_path=filename,
            pid='edi.3.1',
            doi='https://doi.org/10.6073/pasta/bf143fa962e1edb822847bc0ee90c2f7'
        )
        assert '"encodingFormat": "text/csv"' in json_ld
        assert '"encodingFormat": "application/octet-stream"' not in json_ld
