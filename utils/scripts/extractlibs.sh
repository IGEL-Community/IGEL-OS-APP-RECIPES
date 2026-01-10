#!/bin/bash
set -x
trap read debug

find . -name "*.deb" | while read LINE
do
  mkdir ${LINE}_dir
  dpkg -x "${LINE}" ${LINE}_dir
done
