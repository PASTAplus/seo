#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: eml

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
    t = list()
    if hasattr(element, "text") and element.text is not None:
        t.append(element.text.strip())
    if hasattr(element, "__iter__"):
        for e in element:
            t.append(flatten(e))
    return (" ".join(t)).strip()


def clean(text):
    return ' '.join(text.split())


class Eml(object):
    def __init__(self, eml: str):
        self._eml = eml.encode('utf-8')
        self._root = etree.fromstring(self._eml)
        self._abstract = self._get_abstract()
        self._creator = self._get_creator_surname()
        self._funding = self._get_funding()
        self._geographic_coverage = self._get_geographic_coverage()
        self._intellectual_rights = self._get_intellectual_rights()
        self._keywords = self._get_keywords()
        self._title = self._get_title()

    def _get_abstract(self):
        abstract = None
        _ = self._root.find('.//dataset/abstract')
        if _ is not None:
            abstract = clean(_.xpath('string()'))
        return abstract

    def _get_creator_surname(self):
        creator = None
        _ = self._root.findall('.//dataset/creator/individualName/surName')
        if len(_) > 0:
            creator = list()
            for surname in _:
                creator.append(clean(surname.text))
        return creator

    def _get_funding(self):
        funding = None
        _ = self._root.find('.//dataset/project/funding')
        if _ is not None:
            funding = clean(_.xpath('string()'))
        return funding

    def _get_geographic_coverage(self):
        gc = None
        _ = self._root.find('.//dataset/coverage/geographicCoverage')
        if _ is not None:
            gc = dict()
            gc['description'] = clean(_.find('.//geographicDescription').text)
            gc['west'] = clean(_.find('.//boundingCoordinates/westBoundingCoordinate').text)
            gc['east'] = clean(_.find('.//boundingCoordinates/eastBoundingCoordinate').text)
            gc['north'] = clean(_.find('.//boundingCoordinates/northBoundingCoordinate').text)
            gc['south'] = clean(_.find('.//boundingCoordinates/southBoundingCoordinate').text)
        return gc

    def _get_intellectual_rights(self):
        ir = None
        _ = self._root.find('.//dataset/intellectualRights')
        if _ is not None:
            ir = clean(_.xpath('string()'))
        return ir

    def _get_keywords(self):
        keywords = None
        _ = self._root.findall('.//dataset/keywordSet/keyword')
        if len(_) > 0:
            keywords = list()
            for keyword in _:
                keywords.append(clean(keyword.text))
        return keywords

    def _get_title(self):
        title = ''
        _ = self._root.find('.//title')
        if _ is not None:
            title = clean(_.xpath('string()'))
        return title

    @property
    def abstract(self):
        return self._abstract

    @property
    def creator(self):
        return self._creator

    @property
    def funding(self):
        return self._funding

    @property
    def geographic_coverage(self):
        return self._geographic_coverage

    @property
    def intellectual_rights(self):
        return self._intellectual_rights

    @property
    def keywords(self):
        return self._keywords

    @property
    def title(self):
        return self._title


def main():
    return 0


if __name__ == "__main__":
    main()
