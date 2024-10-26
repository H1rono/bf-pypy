#!/usr/bin/env bash

set -eux -o pipefail

ARGC=$#

if [ $ARGC -lt 1 ] ; then
cat - << 'EOF'
usage: translate.sh [<rpython opts>...] <target path>
EOF
exit 1
fi

ARGV=("$@")
CWD="$(pwd)"
OPTS=("${ARGV[@]:0:${#ARGV[@]}-1}")
TARGET="$(realpath "${ARGV[-1]}")"
TARGET_DIR="$(dirname "$TARGET")"
TARGET_FILE="$(basename "$TARGET")"

cd "$TARGET_DIR"
pypy -m rpython "${OPTS[@]}" "$TARGET_FILE"
