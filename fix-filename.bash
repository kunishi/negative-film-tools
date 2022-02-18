#!/bin/bash

exiftool -d '%Y%m%d_%H%M_%%f.%%e' '-filename<createdate' "$@"
