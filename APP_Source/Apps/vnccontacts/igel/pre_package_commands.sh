#!/bin/bash

mkdir -p "%root%/etc/vnccontacts"
cat <<"EOF" > "%root%/etc/vnccontacts/vnccontacts-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="vnccontacts_${1}"

# App Path
APP_PATH="/services/vnccontacts"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/VNCcontactsplus.AppImage /usr/bin/vnccontacts
ln -sv ${APP_PATH}/VNCcontactsplus.AppImage /usr/bin/VNCcontacts

echo "Finished" | $LOGGER

EOF
