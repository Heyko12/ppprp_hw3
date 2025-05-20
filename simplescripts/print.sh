#!/bin/bash

find . \
  -type f \
  ! -path "./.git/*" \
  ! -name "REDME.md" \
  ! -name "TASK.md" \
  ! -path "./simplesirvice/*" \
  ! -path "./istio-1.20.0/*" \
  | sort | while read -r file; do
    echo "===== $file ====="
    cat "$file"
    echo
done