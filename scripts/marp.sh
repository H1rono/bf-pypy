#!/usr/bin/env bash

set -eu -o pipefail

mkdir -p tmp

# FIXME: avoid using python3
if [ $# -ne 1 ] || python3 -c "from sys import exit; exit('$1' in ['build', 'watch'])" ; then
cat - << 'EOF'
usage: marp.sh [ build | watch ]
EOF
exit 1
fi

case "$1" in
	build )
		marp slide.md --output tmp/slide.pdf
	;;
	watch )
		marp slide.md --watch --output tmp/slide.pdf
	;;
	* )
		: unreachable
		exit 1
	;;
esac
