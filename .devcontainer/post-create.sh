#!/usr/bin/env bash

set -eux -o pipefail

sudo chmod +rx /opt/pypy/lib
yarn global add @marp-team/marp-cli
