#!/bin/bash

for file in "$@"; do
    basename=`basename "$file"`
    dirname=`dirname "$file"`
    replaced=`echo "$basename" | sed -e 's/^[0-9]*_[0-9]*_\(.*\)$/\1/'`
    echo "$basename -> $replaced"
    mv "$file" "$dirname/$replaced"
done
