#!/bin/bash
#set -x
#trap read debug

#
# Version: Fri Feb 13 10:37:01 AM MST 2026
#
# ServiceNow Agent Client Collector postinst
#

ACTION="snowacc_postinst"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting - Configure snowacc" | $LOGGER

PROGNAME=`basename $0`

APP_PATH="/services/snowacc"
APP_PATH_RW="/services_rw/snowacc"

ETC_DIR="${APP_PATH}/etc"

SHARE_DIR="${APP_PATH}/usr/share"
VAR_DIR="${APP_PATH}/var"
CACHE_DIR="${APP_PATH_RW}/var/cache"
LOG_DIR="${APP_PATH_RW}/var/log"
RUN_DIR="${APP_PATH_RW}/var/run"

ETC_SN_DIR=$ETC_DIR/servicenow
SHARE_SN_DIR=$SHARE_DIR/servicenow
CACHE_SN_DIR=$CACHE_DIR/servicenow
LOG_SN_DIR=$LOG_DIR/servicenow
RUN_SN_DIR=$RUN_DIR/servicenow

INSTALLER_DIR=$SHARE_SN_DIR/agent-client-collector
EMBEDDED_DIR=$INSTALLER_DIR/embedded
EMBEDDED_BIN_DIR=$EMBEDDED_DIR/bin
EMBEDDED_SHARE_DIR=$EMBEDDED_DIR/share

PID_DIR=$RUN_SN_DIR/agent-client-collector
TMP_DIR=$CACHE_SN_DIR/agent-client-collector

CONFIG_DIR=$ETC_SN_DIR/agent-client-collector
CONFD_DIR=$CONFIG_DIR/conf.d
CERT_DIR=$CONFIG_DIR/cert
CHECK_ALLOW_LIST_DIR=$CONFIG_DIR/check-allow-list.json.default
PLUGINS_DIR=$CONFIG_DIR/plugins
EXTENSIONS_DIR=$CONFIG_DIR/extensions
CONFIG_FILE=$CONFIG_DIR/acc.yml

DEFAULTS_DIR=$ETC_DIR/default

LOG_FILE=$LOG_SN_DIR/agent-client-collector/acc.log
LOG_LEVEL=info

OPTIONS="-c $CONFIG_FILE -d $CONFD_DIR -e $EXTENSIONS_DIR -l $LOG_FILE -L $LOG_LEVEL"

SENSU_PATHS=$EMBEDDED_BIN_DIR:$PATH:$PLUGINS_DIR:$HANDLERS_DIR
SENSU_GEM_PATHS=$EMBEDDED_DIR/lib/ruby/gems/2.2.0:$GEM_PATH

SYSV_SCRIPTS_EXIST=false

SN_USER=servicenow
SN_GROUP=servicenow

chown_sn_dirs()
{
	chown -R $SN_USER:$SN_GROUP $SHARE_SN_DIR
	chown -R $SN_USER:$SN_GROUP $ETC_SN_DIR
	chown -R $SN_USER:$SN_GROUP $LOG_SN_DIR
	chown -R $SN_USER:$SN_GROUP $RUN_SN_DIR
	chown -R $SN_USER:$SN_GROUP $CACHE_SN_DIR
	chown -R $SN_USER:$SN_GROUP $CERT_DIR/servicenow
	chown -R $SN_USER:$SN_GROUP $CERT_DIR/customer
	chown -R $SN_USER:$SN_GROUP $CERT_DIR/cnc
}

chmod_sn_dirs()
{
	# Ensure all relevant files/directories with correct permissions.
	find $SHARE_SN_DIR -type d -exec chmod 755 '{}' '+'
	find $CACHE_SN_DIR -type d -exec chmod 755 '{}' '+'
	find $LOG_SN_DIR -type d -exec chmod 755 '{}' '+'
	find $ETC_SN_DIR -type d -exec chmod 755 '{}' '+'
	find $CERT_DIR -type d -exec chmod 555 '{}' '+'
	find $CERT_DIR/customer -type d -exec chmod 755 '{}' '+'
	find $CERT_DIR/servicenow -type d -exec chmod 755 '{}' '+'
	find $CERT_DIR/cnc -type d -exec chmod 755 '{}' '+'

	chmod_sn_files
	chmod_sn_exes
}

chmod_sn_files()
{
  find $SHARE_SN_DIR -type f -exec chmod 644 '{}' '+'
  find $ETC_SN_DIR -type f -exec chmod 600 '{}' '+'
  find $CERT_DIR -type f -exec chmod 400 '{}' '+'
  find $CHECK_ALLOW_LIST_DIR -type f -exec chmod 400 '{}' '+'
}

chmod_sn_exes()
{
	chmod 755 $INSTALLER_DIR/bin/*
	chmod 755 $EMBEDDED_BIN_DIR/*
}

create_ser_number_file()
{
	
	if ! [ -x "$(command -v dmidecode)" ]; then
	  echo '' > $INSTALLER_DIR/serial_number.txt | $LOGGER
	else
	  dmidecode -s system-serial-number > $INSTALLER_DIR/serial_number.txt
	fi

	chmod 0644 $INSTALLER_DIR/serial_number.txt
	chown $SN_USER:$SN_GROUP $INSTALLER_DIR/serial_number.txt
}

ln -svf ${APP_PATH}/usr/share/servicenow /usr/share/servicenow
ln -svf ${APP_PATH}/etc/servicenow /etc/servicenow

cp -p ${APP_PATH}/etc/servicenow/agent-client-collector/check-allow-list.json.default ${APP_PATH}/etc/servicenow/agent-client-collector/check-allow-list.json

cp -p ${APP_PATH}/etc/servicenow/agent-client-collector/acc.yml.example ${APP_PATH}/etc/servicenow/agent-client-collector/acc.yml

chown_sn_dirs
chmod_sn_dirs
create_ser_number_file

ACC_API_KEY=$(getsysvalue app.snowacc.config.acc-api-key)
ACC_MID=$(getsysvalue app.snowacc.config.acc-mid)

ACC_FILE="${APP_PATH}/etc/servicenow/agent-client-collector/acc.yml"
SEARCH_ACC_MID="wss://127.0.0.1:8800/ws/events"

# Use sed to replace ACC_MID
echo "ACC_API_KEY: ${ACC_API_KEY}" | $LOGGER
sed -i "s|$SEARCH_ACC_MID|$ACC_MID|g" "$ACC_FILE"

# Use sed to replace ACC_API_KEY
echo "ACC_MID: ${ACC_MID}" | $LOGGER
sed -i "s/api-key: \"\"/api-key: \"${ACC_API_KEY}\"/" "$ACC_FILE"

echo "Finished - Configure snowacc" | $LOGGER

exit 0
EOF
