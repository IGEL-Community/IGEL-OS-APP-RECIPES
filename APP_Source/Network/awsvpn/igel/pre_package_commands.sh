#!/bin/bash

mkdir -p "%root%/etc/awsvpn"
cat <<"EOF" > "%root%/etc/awsvpn/awsvpn-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="awsvpn_${1}"

# App Path
APP_PATH="/services/awsvpn"
OVPN_FILE_PATH="/userhome/.config/AWSVPNClient"


LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_PATH}/opt/awsvpnclient /opt/awsvpnclient | $LOGGER

if ! ls ${OVPN_FILE_PATH}/*.ovpn >/dev/null 2>&1; then
  cp ${APP_PATH}/*.ovpn ${OVPN_FILE_PATH}
  chmod a+r ${OVPN_FILE_PATH}/*.ovpn
fi

OPENVPN_PATH=/services/awsvpn/opt/awsvpnclient/Service/Resources/openvpn
pushd $OPENVPN_PATH
export LD_LIBRARY_PATH=$OPENVPN_PATH
$OPENVPN_PATH/openssl \
    fipsinstall \
    -out /services/awsvpn/opt/awsvpnclient/Service/Resources/openvpn/fipsmodule.cnf \
    -module $OPENVPN_PATH/fips.so | $LOGGER

echo "Finished" | $LOGGER

EOF

