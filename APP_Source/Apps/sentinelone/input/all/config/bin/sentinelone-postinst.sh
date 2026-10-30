#!/bin/bash
#set -x
#trap read debug

ACTION="sentinelone_postinst"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Starting"

#Vars
APP_PATH="/services/sentinelone"
APP_PATH_RW="/services_rw/sentinelone"
APP_NAME="sentinelone"
GROUP_NAME="sentinelone"
USER_NAME="sentinelone"

# Create application symlink only if it does not already exist
if [[ ! -L "/opt/${APP_NAME}" ]]; then
    ln -sv "${APP_PATH}/opt/${APP_NAME}" "/opt/${APP_NAME}"
else
    echo "Symlink /opt/${APP_NAME} already exists"
fi

# Create read / write configuration directory only if it does not exist
if [[ ! -d "${APP_PATH_RW}/configuration" ]]; then
    mkdir -pv "${APP_PATH_RW}/configuration"
else
    echo "Directory ${APP_PATH_RW}/configuration already exists"
fi

# Remove configuration directory if it exists
if [[ -d "/opt/${APP_NAME}/configuration" ]]; then
    rm -rfv "/opt/${APP_NAME}/configuration"
else
    echo "/opt/${APP_NAME}/configuration does not exist"
fi

# Create configuration symlink only if it does not already exist
if [[ ! -L "/opt/${APP_NAME}/configuration" ]]; then
    ln -sv "${APP_PATH_RW}/configuration" "/opt/${APP_NAME}/configuration"
else
    echo "Symlink /opt/${APP_NAME}/configuration already exists"
fi

# Create installation_params.json file in the configuration directory
if [[ ! -f "${APP_PATH_RW}/configuration/installation_params.json" ]]; then
    echo "Creating installation_params.json in ${APP_PATH_RW}/configuration"
    cat << EOF > "${APP_PATH_RW}/configuration/installation_params.json"
{
    "PACKAGE_TYPE": "deb"
}
EOF
fi

# Set ownership
chown -R -L ${USER_NAME}:${GROUP_NAME} "${APP_PATH}/opt/sentinelone"
chown -R root:${GROUP_NAME} "${APP_PATH}/opt/sentinelone/bin"

SITE_TOKEN=$(getsysvalue app.${APP_NAME}.config.site-token)

if [ -n "$SITE_TOKEN" ]; then
  #
  # If enrolling, may need to figure out how to handle the changed files / folders after enrollment.
  #
  if [ ! -f /services_rw/${APP_NAME}/enrolled ]; then
    echo "Agent service registered successfully"
    /opt/${APP_NAME}/bin/sentinelctl control set-service-type systemd
    echo "SentinelOne Agent is not enrolled, enrolling now..."
    /opt/${APP_NAME}/bin/sentinelctl management token set $SITE_TOKEN
    echo $(date) > /services_rw/${APP_NAME}/enrolled
  else
    echo "SentinelOne Agent is already enrolled, skipping enrollment."
  fi
fi

echo "Finished"

