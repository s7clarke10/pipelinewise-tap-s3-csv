#!/bin/env/python

import os

from subprocess import call


if __name__ == '__main__':
    if 'GITHUB_ACTIONS' in os.environ:
        rc = call('pytest tests/integraion')
        raise SystemExit(rc)
