#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: utility

:Synopsis:

:Author:
    servilla

:Created:
    8/27/18
"""
import daiquiri

logger = daiquiri.getLogger('utility: ' + __name__)


def pid_triple(pid: str):
    _ = pid.strip().split('.')
    return _[0], _[1], _[2]


def main():
    return 0


if __name__ == "__main__":
    main()
