#!/bin/bash

scripts="autotone autowhite"

for file in $scripts; do
  curl -o $file "http://www.fmwconcepts.com/imagemagick/downloadcounter.php?scriptname=$file&dirname=$file" && \
    install -c -m 755 $file /usr/local/bin && \
    rm -f $file
done
