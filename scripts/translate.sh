#!/usr/bin/env bash

set -eux -o pipefail

if [ $# -lt 2 ] ; then
cat - << 'EOF'
usage: translate.sh <target path>
EOF
exit 1
fi

CWD="$(pwd)"
TARGET="$(realpath "$1")"
TARGET_DIR="$(dirname "$TARGET")"
TARGET_FILE="$(basename "$TARGET")"

cd "$TARGET_DIR"
pypy -m rpython "$TARGET_FILE"
