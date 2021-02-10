#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: __init__

:Synopsis:

:Author:
    servilla

:Created:
    3/16/18
"""

import logging
import os
import sys


import daiquiri


sys.path.insert(0, os.path.abspath('../src'))

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + '/tests.log'
daiquiri.setup(level=logging.DEBUG,
               outputs=(daiquiri.output.File(logfile), 'stdout',))


def main():
    return 0


if __name__ == "__main__":
    main()
