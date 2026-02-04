#!/bin/bash
#set -x
#trap read debug

TV_RW_FOLDER="/services_rw/teamviewerqs/teamviewerqs"

ACTION="teamviewerqs"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

if [ ! -d ${TV_RW_FOLDER} ]; then
  echo "Directory ${TV_RW_FOLDER} does not exist" | $LOGGER
  echo "Setting up ${TV_RW_FOLDER}" | $LOGGER
  /bin/cp -R /services/teamviewerqs/teamviewerqs /services_rw/teamviewerqs
  /bin/chown -R user:users /services_rw/teamviewerqs/teamviewerqs
  /bin/chmod -R 755 /services_rw/teamviewerqs/teamviewerqs
else
  echo "Directory ${TV_RW_FOLDER} exists. Nothing to do" | $LOGGER
fi