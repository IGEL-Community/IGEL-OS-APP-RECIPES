#!/bin/bash

mkdir -p "%root%/etc/appspace"
cat <<"EOF" > "%root%/etc/appspace/appspace-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="appspace_${1}"

# App Path
APP_PATH="/services/appspace"
APP_PATH_RW="/services_rw/appspace"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

# Link to the binary
ln -svf ${APP_PATH}/opt/Appspace\ App/appspace-app /usr/bin/appspace-app | $LOGGER

# Link to userhome Appspace App
ln -svf ${APP_PATH_RW}/userhome/.config/Appspace_App /userhome/.config/Appspace\ App

# SUID chrome-sandbox for Electron 5+
chmod 4755 ${APP_PATH}/opt/Appspace\ App/chrome-sandbox | $LOGGER

echo "Finished" | $LOGGER

EOF

