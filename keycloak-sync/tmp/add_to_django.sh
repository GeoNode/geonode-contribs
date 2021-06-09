#!/bin/bash

SRC_DIR=/usr/src/my_geonode/my_geonode

IFS=$'\n'; set -f
for f in $(find /tmp/additions/ -name '*.py')
do
    FN=$(basename $f)
    cat $f >> $SRC_DIR/$FN
    echo Added from $f to $SRC_DIR/$FN
done
unset IFS; set +f
