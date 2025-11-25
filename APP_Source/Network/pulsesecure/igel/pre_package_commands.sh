#!/bin/bash

mkdir -p "%root%/etc/pulsesecure"
cat <<"EOF" > "%root%/etc/pulsesecure/pulsesecure-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="pulsesecure_${1}"

# App Path
APP_PATH="/services/pulsesecure"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_PATH}/opt/pulsesecure /opt/pulsesecure
ln -svf ${APP_PATH}/var/lib/pulsesecure /var/lib/pulsesecure

setfacl -d -m g::r ${APP_PATH}/var/lib/pulsesecure/pulse
setfacl -d -m o::r ${APP_PATH}/var/lib/pulsesecure/pulse

echo "Finished" | $LOGGER

EOF

