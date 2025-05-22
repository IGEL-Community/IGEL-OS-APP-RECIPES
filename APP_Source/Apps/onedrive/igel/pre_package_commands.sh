#!/bin/bash
#set -x
#trap read debug

mkdir -p "%root%/etc/onedrive"
cat <<"EOF" > "%root%/etc/onedrive/onedrive-init.sh"
#!/bin/bash
set -x
#trap read debug

ACTION="onedrive_${1}"

# App Path
APP_PATH="/services/onedrive"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

#ln -sv /services_rw/onedrive/userhome/.config/onedrive /userhome/.config/onedrive | $LOGGER
#unlink /userhome/.config/onedrive
#ln -sv /services_rw/onedrive/OneDrive /userhome/OneDrive | $LOGGER

echo "Finished" | $LOGGER

EOF
