#!/bin/bash
#set -x
#trap read debug

FOLDER="EXTRACTED"

mkdir -p ${FOLDER}

find . -name "*.deb" | while read LINE
do
  dpkg -x "${LINE}" ${FOLDER}
done
