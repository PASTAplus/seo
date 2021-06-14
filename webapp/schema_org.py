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
            "logo": Config.LOGO_EDI,
        }

        if eml.abstract is not None:
            json_ld["description"] = eml.abstract[:5000]
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
            "logo": Config.LOGO_EDI,
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
            json_ld["identifier"] = {
                "@id": f"https://doi.org/{doi[4:]}",
                "@type": "PropertyValue",
                "propertyID": "https://registry.identifiers.org/registry/doi",
                "value": doi,
                "url": f"https://doi.org/{doi[4:]}"
            }

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


def repository(raw: str = None) -> str:
    json_ld = dict()
    json_ld["@context"] = {"@vocab": "https://schema.org/"}
    json_ld["@type"] = ["Service", "Organization", "ResearchProject"]
    json_ld["@id"] = Config.URL_EDI
    json_ld["identifier"] = [
        {
            "@type": "PropertyValue",
            "name": "Re3data DOI: 10.17616/R3D60K",
            "propertyID": "https://registry.identifiers.org/registry/doi",
            "value": "doi:10.17616/R3D60K",
            "url": "https://doi.org/10.17616/R3D60K"
        },
        {
            "@type": "PropertyValue",
            "name": "FAIRsharing.org DOI: 10.25504/fairsharing.xd3wmy",
            "propertyID": "https://registry.identifiers.org/registry/doi",
            "value": "doi:10.25504/fairsharing.xd3wmy",
            "url": "https://doi.org/10.25504/fairsharing.xd3wmy"
        },
    ]
    json_ld["name"] = "EDI"
    json_ld["legalName"] = "Environmental Data Initiative"
    json_ld["description"] = Config.DESCRIPTION_EDI
    json_ld["url"] = Config.URL_EDI
    json_ld["email"] = Config.EMAIL_EDI
    json_ld["logo"] = Config.LOGO_EDI
    json_ld["funder"] = {"@type": "Organization", "name": "U.S. National Science Foundation"}
    json_ld["sameAs"] = [
        "https://doi.org/10.17616/R3D60K",
        "https://www.re3data.org/repository/r3d100010272",
        "https://isni.org/isni/0000000495505609",
        "urn:node:EDI"
    ]

    j = json.dumps(json_ld, indent=2)
    if raw in ("t", "T", "true", "True", "TRUE"):
        response = j
    else:
        response = f"{open_tag}{j}{close_tag}"

    return response
