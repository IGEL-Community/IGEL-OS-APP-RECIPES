#!/bin/bash

mkdir -p "%root%/etc/vnctask"
cat <<"EOF" > "%root%/etc/vnctask/vnctask-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="vnctask_${1}"

# App Path
APP_PATH="/services/vnctask"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/VNCtask.linux.AppImage /usr/bin/vnctask
ln -sv ${APP_PATH}/VNCtask.linux.AppImage /usr/bin/VNCtask

echo "Finished" | $LOGGER

EOF
