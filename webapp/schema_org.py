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
from typing import Union
from mimetypes import guess_type

import requests
from lxml import etree
from soso.main import convert

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
                doi=doi,
                pasta=pasta,
                portal=portal,
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


def convert_eml_to_schema_org(file_path: str, pid: str, doi: str, pasta: str,
                              portal: str) -> str:
    """Convert EML to Schema.org JSON-LD

    :param file_path: Path to the data package metadata file.
    :param pid: Data package identifier (scope.identifier.revision).
    :param doi: Data package Digital Object Identifier. Must be URL
        prefixed.
    :param pasta: PASTA base URI.
    :param portal: Data portal base URI.
    :returns: JSON-LD string.
    """
    metadata = etree.parse(file_path)

    # Create properties that can't be derived from the EML record
    scope, identifier, revision = pid_triple(pid)
    uri = (f"{portal}/mapbrowse?scope={scope}&identifier={identifier}&"
           f"revision={revision}")
    is_accessible_for_free = True
    provider = {"@id": "https://edirepository.org"}
    publisher = {"@id": "https://edirepository.org"}
    identifier = get_identifier(doi)
    try:
        citation = generate_citation(pid, portal)
    except requests.exceptions.ConnectionError:
        citation = None

    # Create properties that are insufficiently defined by the soso package
    subject_of = get_subject_of(
        file_path=file_path,
        metadata=metadata,
        pasta=pasta
    )
    distribution = get_distribution(metadata=metadata)

    # Call the convert function with the additional properties
    additional_properties = {
        "url": uri,
        "version": revision,
        "isAccessibleForFree": is_accessible_for_free,
        "citation": citation,
        "provider": provider,
        "publisher": publisher,
        "identifier": identifier,
        "subjectOf": subject_of,
        "distribution": distribution,
        "pasta": pasta,  # PASTA base URI for the subjectOf contentUrl
    }
    res = convert(
        file=file_path,
        strategy="EML",
        **additional_properties
    )

    return res


def get_subject_of(file_path: str, metadata: etree.ElementTree,
                   pasta: str) -> Union[dict, None]:
    """
    :param file_path: Path to the data package metadata file.
    :param metadata: file_path as an XML tree.
    :param pasta: PASTA base URI.
    :returns: The subjectOf property for the JSON-LD record.
    """
    scope, identifier, revision, _ = os.path.basename(file_path).split(".")
    encoding_format = get_encoding_format(metadata)
    date_modified = get_date_modified(metadata)
    if encoding_format and date_modified:
        subject_of = {
            "@type": "DataDownload",
            "name": "EML metadata for dataset",
            "description": "EML metadata describing the dataset",
            "encodingFormat": encoding_format,
            "contentUrl": f"{pasta}/metadata/eml/{scope}/{identifier}/"
                          f"{revision}",
            "dateModified": date_modified,
        }
        return subject_of
    return None


def get_distribution(metadata: etree.ElementTree) -> list:
    """
    :param metadata: The metadata object as an XML tree.
    :returns: The distribution property for the JSON-LD record.
    """
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
        for item in metadata.xpath(f".//{data_entity}"):
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
    return distribution


def get_identifier(doi: str) -> Union[dict, None]:
    """
    :param doi: The DOI for the data package.
    :returns: The identifier property for the JSON-LD record.
    """
    if doi is not None:  # development and staging environments don't have DOIs
        identifier = {  # DOI is more informative than the packageId
            "@id": doi,
            "@type": "PropertyValue",
            "propertyID": "https://registry.identifiers.org/registry/doi",
            "value": doi.split("https://doi.org/")[1],
            "url": doi
        }
    else:
        identifier = None
    return identifier


def get_content_size(data_entity_element: etree._Element) -> Union[str, None]:
    """
    :param data_entity_element: The data entity element to get the content
        size from.
    :returns: The content size of a data entity element.
    """
    size_element = data_entity_element.xpath(".//physical/size")
    if size_element:
        size = size_element[0].text
        unit = size_element[0].get("unit")
        if size and unit:
            return size + " " + unit
        return size
    return None


def get_content_url(data_entity_element: etree._Element) -> Union[str, None]:
    """
    :param data_entity_element: The data entity element to get the content
        url from.
    :returns: The content url for a data entity element.
    """
    url_element = data_entity_element.xpath(".//distribution/online/url")
    if url_element:
        if url_element[0].get("function") != "information":
            return url_element[0].text
    return None


def get_data_entity_encoding_format(
    data_entity_element: etree._Element,
) -> Union[str, None]:
    """
    :param data_entity_element: The data entity element to get the encoding
        format from.
    :returns: The encoding format (as a MIME type) for a data entity element.
    """
    object_name = data_entity_element.findtext(".//physical/objectName")
    if object_name:
        encoding_format = guess_type(object_name, strict=False)[0]
    else:
        encoding_format = None
    return encoding_format


def get_checksum(data_entity_element: etree._Element) -> Union[list, None]:
    """
    :param data_entity_element: The data entity element to get the checksum(s)
        from.
    :returns: A list of dictionaries formatted as spdx:Checksum, for each
        method attribute of the authentication element containing a
        spdx:algorithm. Otherwise, None.
    """
    checksum = []
    for item in data_entity_element.xpath(".//physical/authentication"):
        if item.get("method") is not None and "spdx.org" in item.get("method"):
            algorithm = item.get("method").split("#")[-1]
            res = {
                "@type": "spdx:Checksum",
                "spdx:checksumValue": item.text,
                "spdx:algorithm": {"@id": "spdx:" + algorithm},
            }
            checksum.append(res)
    if len(checksum) == 0:
        checksum = None
    return checksum


def get_encoding_format(metadata: etree.ElementTree) -> list:
    """
    :param metadata: The metadata object as an XML tree.
    :returns: The encoding format of an EML metadata record.
    """
    schema_location = metadata.getroot().nsmap.get("eml", None)
    encoding_format = ["application/xml", schema_location]
    return encoding_format


def get_date_modified(metadata: etree.ElementTree) -> Union[str, None]:
    """
    :param metadata: The metadata object as an XML tree.
    :returns: The date modified of an EML metadata record.
    """
    date_modified = metadata.findtext(".//dataset/pubDate")
    return date_modified


def generate_citation(pid: str, portal: str) -> str:
    """
    :param pid: Data package identifier (scope.identifier.revision).
    :param portal: The portal base URL for which the citation will be
        generated.
    :returns: The citation for the data package formatted to ESIP conventions.
    """
    # Determine the environment based on the portal URL
    if "portal-d" in portal:
        env = "development"
    elif "portal-s" in portal:
        env = "staging"
    else:
        env = "production"
    url = f"https://cite.edirepository.org/cite/{pid}"
    parameters = {"env": env, "style": "ESIP"}
    if "knb-lter-and" in pid:  # some scopes want organizations ignored
        parameters["ignore"] = "ORGANIZATIONS"
    r = requests.get(url, params=parameters)
    if r.status_code == requests.codes.ok:
        citation = r.text
    else:
        raise requests.exceptions.ConnectionError()
    return citation
