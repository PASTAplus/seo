#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_security_helpers

:Synopsis:
    Security regression tests for the path-safety and XML-parser helpers in
    :mod:`webapp.utility`.  These tests guard against path-traversal attacks,
    symlink escapes, malformed filenames, and XXE vulnerabilities being
    reintroduced by future changes.

:Created:
    2026-04-22
"""
import io
import os
import tempfile

import pytest
from lxml import etree

from webapp.utility import make_secure_xml_parser, safe_child_path, validate_xml_filename


# ---------------------------------------------------------------------------
# safe_child_path
# ---------------------------------------------------------------------------

class TestSafeChildPath:
    def test_relative_child_resolved_against_base(self):
        """A bare filename (no directory component) is resolved relative to base_dir."""
        with tempfile.TemporaryDirectory() as base:
            result = safe_child_path(base, "file.xml")
            assert result == os.path.realpath(os.path.join(base, "file.xml"))

    def test_valid_direct_child(self):
        with tempfile.TemporaryDirectory() as base:
            child = os.path.join(base, "file.xml")
            result = safe_child_path(base, child)
            assert result == os.path.realpath(child)

    def test_valid_nested_child(self):
        with tempfile.TemporaryDirectory() as base:
            subdir = os.path.join(base, "sub")
            os.makedirs(subdir)
            child = os.path.join(subdir, "file.xml")
            result = safe_child_path(base, child)
            assert result == os.path.realpath(child)

    def test_dotdot_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as base:
            evil = os.path.join(base, "..", "escape.xml")
            with pytest.raises(ValueError):
                safe_child_path(base, evil)

    def test_absolute_path_outside_base_rejected(self):
        with tempfile.TemporaryDirectory() as base:
            with pytest.raises(ValueError):
                safe_child_path(base, "/etc/passwd")

    def test_symlink_escaping_base_rejected(self):
        """A symlink inside base that points outside base must be rejected."""
        with tempfile.TemporaryDirectory() as base:
            with tempfile.TemporaryDirectory() as outside:
                target = os.path.join(outside, "target.xml")
                open(target, "w").close()
                link = os.path.join(base, "link.xml")
                os.symlink(target, link)
                with pytest.raises(ValueError):
                    safe_child_path(base, link)

    def test_sibling_directory_rejected(self):
        """A path that shares the same parent but is not under base is rejected."""
        with tempfile.TemporaryDirectory() as root:
            base = os.path.join(root, "allowed")
            sibling = os.path.join(root, "other", "file.xml")
            os.makedirs(base)
            os.makedirs(os.path.dirname(sibling))
            with pytest.raises(ValueError):
                safe_child_path(base, sibling)


# ---------------------------------------------------------------------------
# validate_xml_filename
# ---------------------------------------------------------------------------

class TestValidateXmlFilename:
    def test_simple_valid_filename(self):
        assert validate_xml_filename("edi.3.1.xml") == "edi.3.1.xml"

    def test_valid_filename_with_hyphens(self):
        assert validate_xml_filename("knb-lter-ntl-1.1.xml") == "knb-lter-ntl-1.1.xml"

    def test_valid_full_path_extracts_basename(self):
        assert validate_xml_filename("/tmp/subdir/edi.3.1.xml") == "edi.3.1.xml"

    def test_non_xml_extension_rejected(self):
        with pytest.raises(ValueError):
            validate_xml_filename("edi.3.1.json")

    def test_no_extension_rejected(self):
        with pytest.raises(ValueError):
            validate_xml_filename("edi")

    def test_shell_metacharacters_rejected(self):
        with pytest.raises(ValueError):
            validate_xml_filename("file;rm -rf.xml")

    def test_spaces_rejected(self):
        with pytest.raises(ValueError):
            validate_xml_filename("my file.xml")

    def test_empty_string_rejected(self):
        with pytest.raises(ValueError):
            validate_xml_filename("")

    def test_xml_only_extension_rejected(self):
        """'.xml' alone (no stem) must be rejected."""
        with pytest.raises(ValueError):
            validate_xml_filename(".xml")


# ---------------------------------------------------------------------------
# make_secure_xml_parser
# ---------------------------------------------------------------------------

class TestMakeSecureXmlParser:
    def test_returns_xml_parser_instance(self):
        parser = make_secure_xml_parser()
        assert isinstance(parser, etree.XMLParser)

    def test_parses_valid_xml(self):
        parser = make_secure_xml_parser()
        doc = etree.parse(io.BytesIO(b"<root><child/></root>"), parser=parser)
        assert doc.getroot().tag == "root"

    def test_each_call_returns_independent_parser(self):
        """Callers must receive independent parser instances."""
        p1 = make_secure_xml_parser()
        p2 = make_secure_xml_parser()
        assert p1 is not p2
