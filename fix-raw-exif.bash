#!/bin/bash

for file in "$@"; do
  echo "$file"
  d=`dirname "$file"`; f=`basename "$file"`; \
  (cd "$d"; \
  src=$f; [[ -f Original/$f ]] && src="Original/$f"; \
  date=`exiftool -s -originalscanframe "$src" | sed -e 's/.*<!-- File created on \([0-9]*\)\.\([0-9]*\)\.\([0-9]*\) \([0-9:]*\)-->.*/\3:\2\:\1 \4/'`; \
  echo $date; \
  exiftool -overwrite_original_in_place \
    "-createdate=\"$date\"" \
    "-datetimeoriginal=\"$date\"" \
    '-exifversion=0231' \
    '-offsettime=+09:00' \
    '-offsettimeoriginal=+09:00' \
    "$f"
)
done
