#!/bin/bash
#set -x
#trap read debug

#
# Version: Fri Feb 13 10:37:01 AM MST 2026
#
# Splashtop-Streamer postinst
#

set -e

ACTION="Splashtop-Streamer_postinst"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

SRS_USER=splashtopstreamer
SRS_GROUP=splashtopstreamer
SRS_HOME=/services/splashtopstreamer/opt/splashtop-streamer
SRS_RW=/services_rw/splashtopstreamer/opt/splashtop-streamer

echo "Starting - Configure Splashtop-Streamer" | $LOGGER

ln -svf /services/splashtopstreamer/opt/splashtop-streamer /opt/splashtop-streamer
ln -svf $SRS_HOME/script/splashtop-streamer /usr/bin/splashtop-streamer

echo "[Splashtop Streamer] Configure streamer" | $LOGGER
chown -R $SRS_USER:$SRS_GROUP $SRS_RW/*
chown -R $SRS_USER:$SRS_GROUP $SRS_HOME/*
mkdir -p $SRS_HOME/config/
chown -R $SRS_USER:$SRS_GROUP $SRS_HOME/config
chmod 2775 $SRS_HOME/config
chmod -f 0664 $SRS_HOME/config/* || true
chmod -f 0770 $SRS_HOME/config/ssl || true
chmod -f 0664 $SRS_HOME/config/ssl/* || true
mkdir -p $SRS_HOME/dump/
chown -R $SRS_USER:$SRS_GROUP $SRS_HOME/dump
chmod 2775 $SRS_HOME/dump
chmod -f 0600 $SRS_HOME/dump/* || true
mkdir -p $SRS_HOME/log/
chown -R $SRS_USER:$SRS_GROUP $SRS_HOME/log
chmod 2775 $SRS_HOME/log
chmod -f 0664 $SRS_HOME/log/* || true
chown $SRS_USER:$SRS_GROUP $SRS_HOME/SRStreamer
chmod 2755 $SRS_HOME/SRStreamer
chown $SRS_USER:$SRS_GROUP $SRS_HOME/SRChat
chmod 2755 $SRS_HOME/SRChat
chown $SRS_USER:$SRS_GROUP $SRS_HOME/SRUtility
chmod 2755 $SRS_HOME/SRUtility

/services/splashtopstreamer/opt/splashtop-streamer/SRUtility --config --key update_need_report --value 1 || true

DEPLOYMENT_CODE=$(getsysvalue app.splashtopstreamer.config.deployment-code)
DEPLOYMENT_CODE_FILE=/opt/splashtop-streamer/config/global.conf

if [ -n "${DEPLOYMENT_CODE}" ]; then
  if [ -f "$DEPLOYMENT_CODE_FILE" ] && grep -q "$DEPLOYMENT_CODE" "$DEPLOYMENT_CODE_FILE"; then
    echo "Deployment code already setup" | $LOGGER
  else
    echo "Adding deployment code ${DEPLOYMENT_CODE}" | $LOGGER
    /services/splashtopstreamer/opt/splashtop-streamer/SRUtility deploy $DEPLOYMENT_CODE
  fi
fi

echo "Finished - Configure Splashtop-streamer" | $LOGGER

exit 0
