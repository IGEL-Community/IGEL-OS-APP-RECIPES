#!/bin/bash

mkdir -p "%root%/etc/virtualhere_server"
cat <<"EOF" > "%root%/etc/virtualhere_server/virtualhere_server-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="virtualhere_server_${1}"

# App Path
APP_PATH="/services/virtualhere_server"
CONFIG_FILE="/wfs/virtualhere_usb_server_config.ini"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

if [ ! -e ${CONFIG_FILE} ]; then
  touch ${CONFIG_FILE}
  chmod 644 ${CONFIG_FILE}
fi

echo "Finished" | $LOGGER

EOF
