#!/bin/bash

set -e

if [[ $# != 1 ]]; then
    echo "Usage: $(basename $0) <ssh target>"
    exit 1
fi

target=$1

src_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

scp -p -r $src_dir/../ifstat.py scripts/* ${target}:/config/scripts

