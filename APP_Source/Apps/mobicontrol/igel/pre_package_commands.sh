#!/bin/bash

mkdir -p "%root%/etc/mobicontrol"
cat <<"EOF" > "%root%/etc/mobicontrol/mobicontrol-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="mobicontrol_${1}"

# App Path
#APP_PATH="/services_rw/mobicontrol/usr/opt/MobiControl"
APP_PATH="/wfs/mobicontrol/usr/opt/MobiControl"
APP_OPT_LINK="/usr/opt/MobiControl"

LOGGER="logger -it ${ACTION}"

if [ ! -d ${APP_PATH} ]; then
  mkdir -p ${APP_PATH}
fi

mkdir -p /usr/opt
ln -svf ${APP_PATH} ${APP_OPT_LINK} | $LOGGER

# Run install.sh for the first time
if [ ! -e ${APP_PATH}/mobicontrol ]; then
  cp /services/mobicontrol/opt/mobicontrol/MCSetup.ini /services/mobicontrol/opt/mobicontrol/installer
  cd /services/mobicontrol/opt/mobicontrol/installer
  /bin/sh install.sh -c -y
fi

# copy mobicontrol to /tmp
#cp /usr/opt/MobiControl/mobicontrol /tmp

echo "Finished" | $LOGGER

EOF