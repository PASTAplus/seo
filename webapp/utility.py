#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: utility

:Synopsis:

:Author:
    servilla

:Created:
    8/27/18
"""
import os
import re

import daiquiri
from lxml import etree

logger = daiquiri.getLogger('utility: ' + __name__)


def safe_child_path(base_dir: str, child: str) -> str:
    """Resolve *child* and verify it is contained within *base_dir*.

    Both paths are resolved with :func:`os.path.realpath` so that symlinks and
    ``..`` components cannot be used to escape the intended directory.  If
    *child* is a relative path it is first joined to *base_dir* so that it
    resolves correctly rather than against the process working directory.

    :param base_dir: Trusted parent directory.
    :param child: Path (absolute or relative to *base_dir*) that must reside
        inside *base_dir*.
    :returns: The resolved absolute path of *child*.
    :raises ValueError: If *child* resolves to a location outside *base_dir*.
    """
    resolved_base = os.path.realpath(base_dir)
    if not os.path.isabs(child):
        child = os.path.join(resolved_base, child)
    resolved_child = os.path.realpath(child)
    if os.path.commonpath([resolved_base, resolved_child]) != resolved_base:
        raise ValueError("Path escapes the allowed base directory")
    return resolved_child


def validate_xml_filename(path: str) -> str:
    """Validate that the basename of *path* is a safe XML filename.

    Acceptable names consist solely of alphanumerics, dots, underscores, and
    hyphens, and must end with ``.xml``.

    :param path: A filename or full path whose basename will be validated.
    :returns: The basename of *path* if it is valid.
    :raises ValueError: If the basename does not match the expected pattern.
    """
    basename = os.path.basename(path)
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.xml", basename):
        raise ValueError("Invalid XML filename")
    return basename


def make_secure_xml_parser() -> etree.XMLParser:
    """Return an :class:`lxml.etree.XMLParser` hardened against common attacks.

    The returned parser disables external-entity resolution (XXE), network
    access, and DTD loading so that untrusted XML documents cannot trigger
    server-side request forgery or entity-expansion attacks.
    """
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
    )


def pid_triple(pid: str):
    _ = pid.strip().split('.')
    return _[0], _[1], _[2]


def main():
    return 0





if __name__ == "__main__":
    main()
