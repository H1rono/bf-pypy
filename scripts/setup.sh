#!/usr/bin/env bash

set -eu -o pipefail

USER_SITE="$(pypy -c 'import site; print site.USER_SITE')"
mkdir -p "$USER_SITE"
cat - << EOF > "$USER_SITE/pypy.pth"
$PWD/pypy
$PWD
EOF
ln -s "$PWD/pypy/rpython" "$USER_SITE/rpython"
pip install -e '.[dev]'
