#!/bin/bash
#set -x
#trap read debug

ACTION="gimp_${1}"

# App Path
APP_PATH="/services/gimp"
APP_NAME=$(ls ${APP_PATH}/GIMP-*.AppImage)

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_NAME} /usr/bin/gimp | $LOGGER

echo "Finished" | $LOGGER
