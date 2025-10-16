#!/bin/bash

mkdir -p "%root%/etc/cisco_secure_client"
cat <<"EOF" > "%root%/etc/cisco_secure_client/cisco_secure_client-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="cisco_secure_client_${1}"

LOGGER="logger -it ${ACTION}"

echo "Start" | $LOGGER

# App Path
APP_PATH="/services/cisco_secure_client"
APP_RW_PATH="/services_rw/cisco_secure_client"

# remove empty (excluded) directory
rm -rf "${APP_PATH}/cisco-secure-client-linux64-*"

# fix permissions to allow user to access folders
chmod o+rx ${APP_PATH}/opt/cisco/secureclient
chmod o+rx ${APP_PATH}/opt/cisco/secureclient/bin
chmod o+rx ${APP_PATH}/opt/cisco/secureclient//bin/plugins
chmod o+rx ${APP_PATH}/opt/cisco/secureclient/lib

echo "Finished" | $LOGGER

EOF