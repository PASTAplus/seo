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
import tempfile

from lxml import etree
import requests
from soso.main import convert
from soso.strategies.eml import (EML, get_content_size, get_content_url,
                                 get_data_entity_encoding_format, get_checksum)
from soso.strategies.eml import get_encoding_format
from soso.utilities import delete_null_values, generate_citation_from_doi

from webapp.utility import pid_triple

from webapp.config import Config
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
        doi_uri = f"{pasta}/doi/eml/{scope}/{identifier}/{revision}"

        # Get EML for the convert function
        r = requests.get(eml_uri)
        if r.status_code == requests.codes.ok:
            eml = r.text
        else:
            raise requests.exceptions.ConnectionError()

        # Get DOI for the convert function
        doi = requests.get(doi_uri)
        if doi.status_code == requests.codes.ok:
            doi = doi.text
            doi = "https://doi.org/" + doi.split(":")[1]  # URL format
        else:
            raise requests.exceptions.ConnectionError()

        # Convert EML to Schema.org JSON-LD - Note, a file path is required
        # for the convert function
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = tmpdir + "/" + pid + ".xml"
            with open(filename, "w") as f:
                f.write(eml)
            json_ld = convert_eml_to_schema_org(
                file_path=filename,
                pid=pid,
                doi=doi
            )

        # Reformat the JSON-LD for readability and write to cache
        json_ld = json.loads(json_ld)
        j = json.dumps(json_ld, indent=2)
        with open(file_path, "w") as fp:
            fp.write(j)

    if raw in ("t", "T", "true", "True", "TRUE"):
        response = j
    else:
        response = f"{open_tag}{j}{close_tag}"

    return response


def convert_eml_to_schema_org(file_path: str, pid: str, doi: str) -> str:
    """Convert EML to Schema.org JSON-LD

    :param file_path: Path to the data package metadata file.
    :param pid: Data package identifier (scope.identifier.revision).
    :param doi: Data package Digital Object Identifier. Must be URL
        prefixed.
    """

    # Add properties that can't be derived from the EML record
    scope, identifier, revision = pid_triple(pid)
    url = ("https://portal.edirepository.org/nis/mapbrowse?scope=" + scope +
           "&identifier=" + identifier + "&revision=" + revision)
    is_accessible_for_free = True
    citation = generate_citation_from_doi(doi, style="apa", locale="en-US")
    provider = {"@id": "https://edirepository.org"}
    publisher = {"@id": "https://edirepository.org"}
    identifier = {  # DOI is more informative than the packageId
        "@id": doi,
        "@type": "PropertyValue",
        "propertyID": "https://registry.identifiers.org/registry/doi",
        "value": doi.split("https://doi.org/")[1],
        "url": doi
    }

    # Modify the get_subject_of method to add the missing contentUrl
    def get_subject_of(self):
        encoding_format = get_encoding_format(self.metadata)
        date_modified = self.get_date_modified()
        if encoding_format and date_modified:
            file_name = self.file.split("/")[-1]
            subject_of = {
                "@type": "DataDownload",
                "name": "EML metadata for dataset",
                "description": "EML metadata describing the dataset",
                "encodingFormat": encoding_format,
                "contentUrl": (
                        "https://pasta.lternet.edu/package/metadata/eml/" +
                        file_name.split(".")[0] + "/" +
                        file_name.split(".")[1] + "/" +
                        file_name.split(".")[2]),
                "dateModified": date_modified,
            }
            return delete_null_values(subject_of)
        return None
    # Override the get_subject_of method of the EML strategy
    EML.get_subject_of = get_subject_of

    # Modify the get_distribution method to set a default encodingFormat when
    # it is missing
    def get_distribution(self):
        distribution = []
        data_entities = [
            "dataTable",
            "spatialRaster",
            "spatialVector",
            "storedProcedure",
            "view",
            "otherEntity",
        ]
        for data_entity in data_entities:
            for item in self.metadata.xpath(f".//{data_entity}"):
                encoding_format = get_data_entity_encoding_format(item)
                if encoding_format is None:  # Default encodingFormat when missing
                    encoding_format = "application/octet-stream"
                data_download = {
                    "@type": "DataDownload",
                    "name": item.findtext(".//entityName"),
                    "description": item.findtext(".//entityDescription"),
                    "contentSize": get_content_size(item),
                    "contentUrl": get_content_url(item),
                    "encodingFormat": encoding_format,
                    "spdx:checksum": get_checksum(item),
                }
                distribution.append(data_download)
        return delete_null_values(distribution)
    # Override the get_distribution method of the EML strategy
    EML.get_distribution = get_distribution

    # Call the convert function with the additional properties
    additional_properties = {
        "url": url,
        "version": revision,
        "isAccessibleForFree": is_accessible_for_free,
        "citation": citation,
        "provider": provider,
        "publisher": publisher,
        "identifier": identifier
    }
    res = convert(
        file=file_path,
        strategy="EML",
        **additional_properties
    )

    return res


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
        {
            "@type": "PropertyValue",
            "name": "Global Research Identifier Database: grid.511300.6",
            "propertyID": "https://registry.identifiers.org/registry/grid",
            "value": "grid.511300.6",
            "url": "https://www.grid.ac/institutes/grid.511300.6"
        },
        {
            "@type": "PropertyValue",
            "name": "Research Organization Registry: ror.org/0330j0z60",
            "propertyID": "https://ror.org",
            "value": "ror.org/0330j0z60",
            "url": "https://ror.org/0330j0z60"
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
