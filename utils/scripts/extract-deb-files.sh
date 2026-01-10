#!/bin/bash
#set -x
#trap read debug

#
# Extract Deb files
#

find . -name "*.deb" | while read LINE
do
  mkdir ${LINE}_dir
  cd ${LINE}_dir
  mkdir control_dir 
  mkdir data_dir
  ar -x  ../${LINE}
  cd control_dir
  tar xvf ../control.tar.*
  cd ..
  cd data_dir
  tar xvf ../data.tar.*
  cd ..
  cd ..
done
