#!/bin/bash

mkdir -p "%root%/etc/vnctalk"
cat <<"EOF" > "%root%/etc/vnctalk/vnctalk-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="vnctalk_${1}"

# App Path
APP_PATH="/services/vnctalk"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/VNCtalk.AppImage /usr/bin/vnctalk
ln -sv ${APP_PATH}/VNCtalk.AppImage /usr/bin/VNCtalk

echo "Finished" | $LOGGER

EOF
