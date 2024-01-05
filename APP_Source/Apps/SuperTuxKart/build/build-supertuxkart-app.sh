#!/bin/bash
#set -x
#trap read debug

# Creating an IGELOS CP
## Development machine Ubuntu (OS12 = 20.04)
CP="supertuxkart"
ZIP_LOC="https://github.com/IGEL-Community/IGEL-Custom-Partitions/raw/master/APP_Packages/Apps"
ZIP_FILE="SuperTuxKart"
APP_NAME="supertuxkart-1.1.0"

VERSION_ID=$(grep "^VERSION_ID" /etc/os-release | cut -d "\"" -f 2)

if [ "${VERSION_ID}" = "20.04" ]; then
  IGELOS_ID="OS12"
else
  echo "Not a valid Ubuntu OS release. OS12 needs 20.04 (focal)."
  exit 1
fi

if ! [ -x "$(command -v igelpkg)" ]; then
  echo "Error: Please install IGEL OS App SDK."
  exit 1
fi

mkdir build_pkg
cd build_pkg

wget ${ZIP_LOC}/${ZIP_FILE}.zip

unzip ${ZIP_FILE}.zip -d custom

cd custom/target/igelpkg

igelpkg build -r focal
igelpkg sign -a -p igelpkg.output/${APP_NAME}.ipkg

mv igelpkg.output/${APP_NAME}.ipkg ../../../..

cd ../../../..
rm -rf build_pkg
