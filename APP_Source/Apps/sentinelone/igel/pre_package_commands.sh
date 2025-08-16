#!/bin/bash

mkdir -p "%root%/etc/sentinelone"
cat <<"EOF" > "%root%/etc/sentinelone/sentinelone-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="sentinelone_${1}"

#Vars
APP_PATH="/services/sentinelone"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -sv ${APP_PATH}/opt/sentinelone /opt/sentinelone

echo "Finished" | $LOGGER

EOF