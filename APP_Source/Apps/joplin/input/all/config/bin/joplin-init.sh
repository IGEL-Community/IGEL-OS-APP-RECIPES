#!/bin/bash
#set -x
#trap read debug

ACTION="joplin_${1}"

# App Path
APP_PATH="/services/joplin"
APP_NAME=$(ls ${APP_PATH}/Joplin-*.AppImage)

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_NAME} /usr/bin/joplin | $LOGGER

echo "Finished" | $LOGGER
