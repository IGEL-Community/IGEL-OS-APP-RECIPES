#!/bin/bash
#set -x
#trap read debug

ACTION="fortidlp_${1}"

LOGGER="logger -it ${ACTION}"

echo "Start" | $LOGGER

# App Path
APP_PATH="/services/fortidlp"
APP_RW_PATH="/services_rw/fortidlp"
JAZZ_PATH="/usr/local/jazz"
JAZZ_ETC_CERT="/etc/jazz/trust.pem"
JAZZ_RUN_SOCK="/var/run/jazz-agent.sock"

FORTIDLP_ENROLLMENT_TOKEN=$(getsysvalue app.fortidlp.config.enrollment-token)

#ln -svf ${APP_PATH}/${JAZZ_PATH} ${JAZZ_PATH} | $LOGGER

if [[ -n "${FORTIDLP_ENROLLMENT_TOKEN}" && ! -f ${JAZZ_ETC_CERT} ]]; then
  echo "Enrolling device" | $LOGGER
  # Loop until the file appears
  while [[ -z $(compgen -G "$JAZZ_RUN_SOCK") ]]; do
      echo "waiting for file $JAZZ_RUN_SOCK" | $LOGGER
      sleep 1
  done
  /services/fortidlp/usr/sbin/jazz-agent enroll -f ${FORTIDLP_ENROLLMENT_TOKEN} | $LOGGER
fi

echo "Finished" | $LOGGER