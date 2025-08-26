#!/bin/bash

mkdir -p "%root%/etc/papercut/config"
cat <<"EOF" > "%root%/etc/papercut/config/client.conf.toml"
#This file will be copied into /wfs/papercut/config for editing
#This file will be copied to /etc/papercut-print-deploy-client folder during unpacking as a conffile.
#refer https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files for more information

EOF

cat <<"EOF" > "%root%/etc/papercut/papercut-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="papercut_${1}"

# IGEL folder
IGEL_FOLDER_RO=/services/papercut
IGEL_FOLDER_RW=/services_rw/papercut
# client config toml
CLIENT_CONFIG_FOLDER=config
TOML=client.conf.toml
WFS_FOLDER=/wfs/papercut
# official package name
PACKAGE_NAME=papercut-print-deploy-client
# root directory of the application
SERVICE_ROOT_DIR=/opt/PaperCutPrintDeployClient
# data dir of the application
SERVICE_DATA_DIR=${SERVICE_ROOT_DIR}/data
# location of the logs for this application
SERVICE_LOG_DIR=/var/log/${PACKAGE_NAME}

LOGGER="logger -it ${ACTION}"

# link file system folder
ln -svf ${IGEL_FOLDER_RO}/${SERVICE_ROOT_DIR} ${SERVICE_ROOT_DIR}

# Use /wfs/papercut/config for files
if [ ! -d ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER} ]; then
  mkdir -p ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}
  cp /etc/papercut/config/client.conf.toml ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}/${TOML}
  chmod -R 755 ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}
  chmod 644 ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}/${TOML}
fi
ln -svf ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}/${TOML} ${SERVICE_DATA_DIR}/${TOML}
# Link file to /etc/papercut-print-deploy-client
ln -svf ${WFS_FOLDER}/${CLIENT_CONFIG_FOLDER}/${TOML} /etc/papercut-print-deploy-client/${TOML}

echo "Finished" | $LOGGER

EOF