#!/bin/bash
#set -x
#trap read debug

#
# Installed Apps
#

tmpfile=$(mktemp)

for app in `igelpkgctl list installed | tail -n +2` ; do
  echo $app > $tmpfile
  igelpkgctl info $app | grep -iE "^summary:|public_version:" | awk -F':' '{print $2}' >> $tmpfile
  paste -d' ' - - - < $tmpfile
done

rm -f $tmpfile