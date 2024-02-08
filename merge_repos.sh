#!/bin/bash

set -e

if [ $# -lt 1 ]; then
  echo "$0 <output_folder>"
  exit 1
fi

output_folder="$1"

rsync -a --exclude '.git' --exclude '.gitmodules' --delete . "$output_folder"
