#!/bin/bash

mkdir -p "%root%/etc/qz-tray"
cat <<"EOF" > "%root%/etc/qz-tray/qz-tray-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="qz_tray_${1}"

# App Path
APP_PATH="/services/qz_tray"
APP_OPT_PATH="/services_rw/qz_tray/opt/qz-tray"
APP_OPT_LINK="/opt/qz-tray"

LOGGER="logger -it ${ACTION}"

chown root:root ${APP_PATH}/qz-tray.run | $LOGGER
chmod 500 ${APP_PATH}/qz-tray.run | $LOGGER

# install qz-tray if it does not exist
if [ ! -e ${APP_OPT_PATH}/qz-tray ]; then
  ${APP_PATH}/qz-tray.run | $LOGGER
  cp -Rp ${APP_OPT_LINK}/* ${APP_OPT_PATH} | $LOGGER
else
  cp -Rp ${APP_OPT_PATH} ${APP_OPT_LINK} | $LOGGER
fi

echo "Finished" | $LOGGER

EOF