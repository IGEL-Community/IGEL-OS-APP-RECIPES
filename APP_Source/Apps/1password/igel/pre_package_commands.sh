#!/bin/bash

mkdir -p "%root%/etc/1password"
cat <<"EOF" > "%root%/etc/1password/1password-init.sh"
#!/bin/bash
set -x
#trap read debug

ACTION="1password_${1}"

# App Path
APP_PATH="/services/1password"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

#
# Add logic here for integrating 1password with browsers
#

#
# Add logic to backup / restore 1password user files
#

# Assumption - This command is ONLY run at boot time!!!

PW="/userhome/.config/1Password"
PW_FILE="${PW}/1password_resources.sqlite"
PW_BACKUP="/userhome/.config/1Password-backup"
PW_BACKUP_FILE="${PW_BACKUP}/1password_resources.sqlite"

# On boot up - copy if it exists
if [ -e ${PW_BACKUP_FILE} ]; then
  rsync -Pav ${PW_BACKUP}/ ${PW} | $LOGGER
  chown -R user:users ${PW} | $LOGGER
fi

# loop forever to sync files
while true
do
  sleep 5
  if [ -e ${PW_FILE} ]; then
    rsync --delete -Pav ${PW}/ ${PW_BACKUP} | $LOGGER
  fi
done

echo "Finished" | $LOGGER

EOF
