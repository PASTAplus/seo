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
from flask import abort, Flask, request
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
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        abort(400)
    else:
        return response

@app.route('/seo/schema/sitemap', methods=['GET', 'POST'])
def sitemap():
    if request.environ['REQUEST_METHOD'] == 'GET':
        # return sitemap.xml
        pass
    else: # POST from PASTA
        # add to sitemap.xml
        remote_address = request.environ['REMOTE_ADDR']
        print(remote_address)
        if remote_address not in Config.WHITE_LIST:
            abort(403)
        else:
            pid = request.get_data().decode('utf-8')
            env = Config.WHITE_LIST[remote_address]
    return "Howdy ho neighbor"


if __name__ == '__main__':
    app.run()
