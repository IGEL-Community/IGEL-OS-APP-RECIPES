#!/bin/bash

mkdir -p "%root%/etc/vncmail"
cat <<"EOF" > "%root%/etc/vncmail/vncmail-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="vncmail_${1}"

# App Path
APP_PATH="/services/vncmail"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/VNCmail.linux.AppImage /usr/bin/vncmail
ln -sv ${APP_PATH}/VNCmail.linux.AppImage /usr/bin/VNCmail

echo "Finished" | $LOGGER

EOF
