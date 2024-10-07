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
from webapp.schema_org import convert_eml_to_schema_org, generate_citation

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
            doi='https://doi.org/10.6073/pasta/bf143fa962e1edb822847bc0ee90c2f7',
            pasta='https://pasta.lternet.edu/package',
            portal='https://portal.edirepository.org/nis',
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
            doi='https://doi.org/10.6073/pasta/bf143fa962e1edb822847bc0ee90c2f7',
            pasta='https://pasta.lternet.edu/package',
            portal='https://portal.edirepository.org/nis',
        )
        assert '"encodingFormat": "text/csv"' in json_ld
        assert '"encodingFormat": "application/octet-stream"' not in json_ld


def test_convert_eml_to_schema_org_uses_correct_environment():
    """Test that the convert_eml_to_schema_org function results in URIs
    pointing to the correct PASTA and portal environments"""
    env = ["", "-s", "-d"]
    for e in env:
        pasta = f"https://pasta{e}.lternet.edu/package"
        portal = f"https://portal{e}.edirepository.org/nis"
        if e == "":  # only production has valid DOIs
            doi = "https://doi.org/10.6073/pasta/bf143fa962e1edb822847bc0ee90c2f7"
        else:
            doi = "https://doi.org/DOI_PLACE_HOLDER"
        json_ld = convert_eml_to_schema_org(
            file_path='tests/data/edi.3.1.xml',
            pid='edi.3.1',
            doi=doi,
            pasta=pasta,
            portal=portal,
        )
        assert pasta in json_ld
        assert portal in json_ld


def test_generate_citation():
    """Test that the generate_citation function generates a citation"""
    res = generate_citation(
        pid="edi.3.1",
        portal="https://portal.edirepository.org/nis"
    )
    assert res is not None

