#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: run

:Synopsis:
 
:Author:
    servilla

:Created:
    8/16/18
"""
import daiquiri
from flask import abort, Flask, request, send_file
import requests

from webapp.config import Config
import webapp.schema_org as schema_org
import webapp.sitemaps_org as sitemaps_org


logger = daiquiri.getLogger('run.py: ' + __name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/seo')
def hello_world():
    return 'Hello on Wheels!'


@app.route('/seo/schema/dataset')
def dataset():
    pid = request.args.get('pid')
    env = request.args.get('env')
    raw = request.args.get('raw')

    try:
        response = schema_org.dataset(pid=pid, env=env, raw=raw)
        return response
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        abort(400)


@app.route('/seo/schema/sitemap', methods=['GET'])
def sitemap():
    if request.environ['REQUEST_METHOD'] == 'GET':
        env = request.args.get('env')

        try:
            sitemap_bundle = sitemaps_org.generate_sitemap_bundle(env=env)
            return send_file(sitemap_bundle)
        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            abort(400)


if __name__ == '__main__':
    app.run()
