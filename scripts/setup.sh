#!/usr/bin/env bash

set -eu -o pipefail

USER_SITE="$(pypy -c 'import site; print site.USER_SITE')"
mkdir -p "$USER_SITE"
cp pypy.pth "${USER_SITE}/pypy.pth"
pip install -e '.[dev]'
