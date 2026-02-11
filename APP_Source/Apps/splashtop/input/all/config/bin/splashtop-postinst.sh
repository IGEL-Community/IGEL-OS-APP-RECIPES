#!/bin/bash
#set -x
#trap read debug

#
# Version: Wed Feb 11 09:02:33 AM MST 2026
#
# Splashtop postinst
#

set -e

ACTION="Splashtop postinst"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting - Configure Splashtop-business" | $LOGGER

ln -svf /services/splashtop/opt/splashtop-business /opt/splashtop-business
ln -svf /opt/splashtop-business/splashtop-business /usr/bin/splashtop-business

chmod a=rwx /opt/splashtop-business/config
chmod a=rwx /opt/splashtop-business/
chmod a=rwx /opt/splashtop-business/log
chmod a=rwx /opt/splashtop-business/dump
chmod a=rwx /opt/splashtop-business/lib

echo "Finished - Configure Splashtop-business" | $LOGGER

exit 0
