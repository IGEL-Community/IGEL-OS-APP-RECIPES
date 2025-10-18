#!/bin/bash

mkdir -p "%root%/etc/ia_vision"
cat <<"EOF" > "%root%/etc/ia_vision/ia_vision-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="ia_vision_${1}"

LOGGER="logger -it ${ACTION}"

echo "Start" | $LOGGER

# App Path
APP_PATH="/services/ia_vision"
APP_RW_PATH="/services_rw/ia_vision"

# fix permissions to allow user to access folders
chmod o+rx ${APP_PATH}/visionclientlauncher
find ${APP_PATH}/visionclientlauncher -type d -exec chmod o+rx {} \;

echo "Finished" | $LOGGER

EOF