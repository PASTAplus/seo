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
from flask import Flask, request

import webapp.schema_org as schema_org


logger = daiquiri.getLogger('run: ' + __name__)


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/schema/dataset')
def schema():
    pid = request.args.get('pid')
    env = request.args.get('env')
    return schema_org.dataset(pid=pid)


if __name__ == '__main__':
    app.run(debug=True)
