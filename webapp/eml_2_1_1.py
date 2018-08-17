#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: eml_2_1_1

:Synopsis:

:Author:
    servilla

:Created:
    8/16/18
"""
import daiquiri
from lxml import etree

logger = daiquiri.getLogger('eml_2_1_1: ' + __name__)


def flatten(element):
    t = ''
    if len(element) == 0:
        return element.text
    else:
        for e in element:
            t += flatten(e)
    return t


def clean(text):
    return ' '.join(text.split())


class Eml(object):
    def __init__(self, eml: str):
        self._eml = eml.encode('utf-8')
        self._root = etree.fromstring(self._eml)
        self._namespaces = {'eml': 'eml://ecoinformatics.org/eml-2.1.1'}
        self._title = self._get_title()
        self._abstract = self._get_abstract()

    def _get_abstract(self):
        abstract = clean(flatten(self._root.xpath('/eml:eml/dataset/abstract', namespaces=self._namespaces)))
        return abstract

    def _get_title(self):
        title = clean(flatten(self._root.xpath('/eml:eml/dataset/title', namespaces=self._namespaces)))
        return title

    @property
    def abstract(self):
        return self._abstract

    @property
    def title(self):
        return self._title


def main():
    return 0


if __name__ == "__main__":
    main()
