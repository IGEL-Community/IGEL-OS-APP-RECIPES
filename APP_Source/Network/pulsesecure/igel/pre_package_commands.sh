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

# MOVE THE FOLLOWING INTO A FINAL DESKTOP COMMAND
# https://igel-community.github.io/IGEL-Docs-v02/Docs/HOWTO-Custom-Commands/
#
# cefRuntime = CEF (Chromium Embedded Framework) runtime, a lightweight
# embedded Chromium browser engine packaged with the Secure Access Client.
#
# CEF allows applications to render modern HTML/JS/CSS content without
# relying on the system browser. In the Secure Access Client, it is used for:
# 
# - Web-based authentication pages (e.g., SAML, OIDC, MFA portals)
# 
# - Embedded UI dialogs that rely on web technologies
# 
# - Displaying captive portal or login forms inside the client
# 
# - Ensuring a consistent and secure browser engine regardless of Linux distribution
#
#
#CEF_INSTALL_ROOT_DIR=/opt
#CEF_INSTALL_DIR=${CEF_INSTALL_ROOT_DIR}/pulsesecure/lib/cefRuntime
#
## if $CEF_INSTALL_DIR is empty
#if [ -z "$(ls -A "$CEF_INSTALL_DIR")" ]; then
#  echo "Downloading and installing CEF (Chromium Embedded Framework)" | $LOGGER
#  #CEF install change path from /tmp to ${APP_PATH}
#  SETUP_CEF=${APP_PATH}/opt/pulsesecure/bin/setup_cef.sh
#  #sed -i -e "s|TMP_DIR=/tmp/cef.download|TMP_DIR=/custom/cef.download|" $SETUP_CEF
#  #sed -i -e "s|CEF_INSTALL_ROOT_DIR=/opt|CEF_INSTALL_ROOT_DIR=/custom/pulse/opt|" $SETUP_CEF
#  #CEF_INSTALL_ROOT_DIR=/opt|CEF_INSTALL_ROOT_DIR=/custom/pulse/opt|" $SETUP_CEF
#  #TMP_DIR=.
#  CEF_INSTALL_ROOT_DIR=/opt
#  CEF_INSTALL_DIR=${CEF_INSTALL_ROOT_DIR}/pulsesecure/lib/cefRuntime
#  CEF_URL=`grep URL= $SETUP_CEF | grep linux | cut -d "=" -f 2`
#  CEF_PACKAGE_NAME=$(grep CEF_PACKAGE_NAME= $SETUP_CEF | cut -d "=" -f 2)
#  tmpdir=$(mktemp -d)
#  wget -O ${tmpdir}/cef64.tar.bz2 $CEF_URL | $LOGGER
#  tar xvf ${tmpdir}/cef64.tar.bz2 -C ${tmpdir} | $LOGGER
#  cp -r ${tmpdir}/${CEF_PACKAGE_NAME}/* ${CEF_INSTALL_DIR}/
#  cp -r $CEF_INSTALL_DIR/Resources/* $CEF_INSTALL_DIR/Release/
#  rm -rf ${tmpdir}"
#fi

echo "Finished" | $LOGGER

EOF

