#!/bin/bash
#set -x
#trap read debug

ACTION="bigfix_postinst"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Starting"

#Vars
APP_PATH="/services/bigfix"
APP_PATH_RW="/services_rw/bigfix"
APP_NAME="bigfix"
APP_NAME_ORIG="BESClient"
APP_ETC="/etc/opt/${APP_NAME_ORIG}"
APP_ACTION_SITE="actionsite.afxm"
APP_VAR="/var/opt/${APP_NAME_ORIG}"
APP_DEFAULT_CONFIG="besclient.config.default"

# Create application symlink only if it does not already exist
if [[ ! -L "/opt/${APP_NAME_ORIG}" ]]; then
    ln -sv "${APP_PATH}/opt/${APP_NAME_ORIG}" "/opt/${APP_NAME_ORIG}"
else
    echo "Symlink /opt/${APP_NAME_ORIG} already exists"
fi

# Create actionsite.afxm symlink only if it does not already exist
if [[ ! -L "${APP_ETC}/${APP_ACTION_SITE}" ]]; then
    mkdir -p "${APP_ETC}"
    ln -sv "${APP_PATH}/${APP_ACTION_SITE}" "${APP_ETC}/${APP_ACTION_SITE}"
else
    echo "Symlink ${APP_ETC}/${APP_ACTION_SITE} already exists"
fi

# Create /var/opt/BESClient symlink only if it does not already exist
if [[ ! -L "${APP_VAR}" ]]; then
    ln -sv "${APP_PATH_RW}${APP_VAR}_rw" "${APP_VAR}"
else
    echo "Symlink ${APP_VAR} already exists"
fi

# Create /var/opt/BESClient/besclient.config.default symlink only if it does not already exist
if [ ! -f "${APP_PATH_RW}/${APP_VAR}/${APP_DEFAULT_CONFIG}" ]; then
    echo "File ${APP_PATH_RW}/${APP_VAR}/${APP_DEFAULT_CONFIG} does not exist"
    cat << "EEOFF" > "${APP_PATH_RW}/${APP_VAR}/${APP_DEFAULT_CONFIG}"
; Sample besclient.config file

[Software\BigFix\EnterpriseClient]
EnterpriseClientFolder         = /opt/BESClient

[Software\BigFix\EnterpriseClient\GlobalOptions]
StoragePath                    = /var/opt/BESClient
LibPath                        = /opt/BESClient/BESLib

[Software\BigFix\EnterpriseClient\Settings\Client\_BESClient_EMsg_File]
value                          = /var/opt/BESClient/besclientdebug.log

[Software\BigFix\EnterpriseClient\Settings\Client\_BESClient_EMsg_Detail]
value                          = 0
EEOFF
fi

# Linking files and folders on proper path
  find ${APP_PATH_RW} -printf "/%P\n" | while read DEST
  do
    if [ ! -z "${DEST}" -a ! -e "${DEST}" ]; then
      # Remove the last slash, if it is a dir
      [ -d $DEST ] && DEST=${DEST%/}
      if [ ! -z "${DEST}" ]; then
        ln -sv "${APP_PATH_RW}/${DEST}" "${DEST}"
      fi
    fi
  done

# fix ownership
#chown root:root /etc/init.d/besclient
#chown root:root -R /opt/BESClient
#chown root:root -R /var/opt/BESClient
#chown root:root -R /lib/systemd/system/besclient.service.d
#chown root:root /var/lib/dpkg/info/besagent.*

echo "Finished"

