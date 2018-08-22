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


logger = daiquiri.getLogger('run.py: ' + __name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/seo')
def hello_world():
    return 'Hello on Wheels!'


@app.route('/seo/schema/dataset')
def schema():
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


if __name__ == '__main__':
    app.run()
