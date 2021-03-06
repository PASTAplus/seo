#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: shchema_org

:Synopsis:

:Author:
    servilla

:Created:
    8/16/18
"""
import json
import os.path

from lxml import etree
import requests

from webapp.config import Config
from webapp.eml import Eml
import webapp.utility as utility

open_tag = '<script type="application/ld+json">\n'
close_tag = "\n</script>"


def dataset(pid: str, env: str = None, raw: str = None):
    if env in ("d", "dev", "development"):
        pasta = Config.PASTA_D
        portal = Config.PORTAL_D
        cache = Config.CACHE_D
    elif env in ("s", "stage", "staging"):
        pasta = Config.PASTA_S
        portal = Config.PORTAL_S
        cache = Config.CACHE_S
    else:
        pasta = Config.PASTA_P
        portal = Config.PORTAL_P
        cache = Config.CACHE_P

    file_path = f"{cache}{pid}.json"

    if os.path.isfile(file_path):
        # Read from cached location
        with open(file_path, "r") as fp:
            j = fp.read()
    else:
        scope, identifier, revision = utility.pid_triple(pid)
        pid_frag = f"{scope}/{identifier}/{revision}"
        eml_uri = f"{pasta}/metadata/eml/{pid_frag}"
        portal_uri = f"{portal}/metadataviewer?packageid={pid}"
        rmd_uri = f"{pasta}/rmd/eml/{scope}/{identifier}/{revision}"

        r = requests.get(eml_uri)
        if r.status_code == requests.codes.ok:
            eml = r.text
        else:
            raise requests.exceptions.ConnectionError()

        eml = Eml(eml=eml)

        json_ld = dict()
        json_ld["@context"] = "http://schema.org"
        json_ld["@type"] = "Dataset"
        json_ld["name"] = eml.title
        json_ld["url"] = portal_uri
        json_ld["publisher"] = {
            "@type": "Organization",
            "@id": Config.URL_EDI,
            "name": "Environmental Data Initiative",
            "description": Config.DESCRIPTION_EDI,
            "url": Config.URL_EDI,
            "email": Config.EMAIL_EDI,
        }

        if eml.abstract is not None:
            json_ld["description"] = eml.abstract
        else:
            json_ld["description"] = eml.title

        if eml.creator is not None:
            creators = list()
            for creator in eml.creator:
                creators.append({"@type": "Person", "familyName": creator})
            json_ld["creator"] = creators

        if eml.funding is not None:
            json_ld["funding"] = {"@type": "Organization", "name": eml.funding}

        if eml.geographic_coverage is not None:
            west = eml.geographic_coverage["west"]
            east = eml.geographic_coverage["east"]
            north = eml.geographic_coverage["north"]
            south = eml.geographic_coverage["south"]

            json_ld["spatialCoverage"] = {
                "@type": "Place",
                "geo": {
                    "@type": "GeoShape",
                    "description": eml.geographic_coverage["description"],
                    "box": f"{south} {east} {north} {west}",
                },
            }

        json_ld["includedInDataCatalog"] = {
            "@type": "DataCatalog",
            "@id": Config.URL_EDI,
            "name": "Environmental Data Initiative",
            "description": Config.DESCRIPTION_EDI,
            "url": portal,
            "funder": {
                "@type": "Organization",
                "name": "U.S. National Science Foundation",
            },
        }

        if eml.keywords is not None:
            json_ld["keywords"] = eml.keywords

        date_published, doi = get_resource_metadata(rmd_uri)
        if date_published is not None:
            json_ld["datePublished"] = date_published
        if doi is not None:
            json_ld["identifier"] = doi

        j = json.dumps(json_ld, indent=2)
        with open(file_path, "w") as fp:
            fp.write(j)

    if raw in ("t", "T", "true", "True", "TRUE"):
        response = j
    else:
        response = f"{open_tag}{j}{close_tag}"

    return response


def get_resource_metadata(rmd_uri: str):
    upload_date = None
    doi = None
    r = requests.get(rmd_uri)
    if r.status_code == requests.codes.ok:
        rmd = etree.fromstring(r.text.encode("utf-8"))
        date_created = rmd.find(".//dateCreated").text
        upload_date = date_created.split(" ")[0]
        doi = rmd.find(".//doi").text
    return upload_date, doi


def main():
    return 0


if __name__ == "__main__":
    main()
