#!/bin/bash

mkdir -p "%root%/etc/ringcentral_horizon_vdi"

cat <<"EOF" > "%root%/etc/ringcentral_horizon_vdi/ringcentral_horizon_vdi-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="ringcentral_horizon_vdi_${1}"

# App Path
APP_PATH="/services/ringcentral_horizon_vdi"

LOGGER="logger -it ${ACTION}"

echo "Start" | $LOGGER

echo "Install plugin for Omnissa Horizon" | $LOGGER
mkdir -p "/usr/lib/omnissa/rdpvcbridge"
ln -sf "${APP_PATH}/opt/RingCentral-App-VdiPlugin/Plugin/x64/libJupVdiPluginBridge.ld.so" "/usr/lib/omnissa/rdpvcbridge/libJupPlugin.so"
ln -sf "${APP_PATH}/opt/RingCentral-App-VdiPlugin" "/opt/RingCentral-App-VdiPlugin"

echo "Finished" | $LOGGER

EOF