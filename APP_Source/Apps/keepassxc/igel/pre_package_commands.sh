#!/bin/bash

mkdir -p "%root%/etc/keepassxc"
cat <<"EOF" > "%root%/etc/keepassxc/keepassxc-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="keepassxc_${1}"

# App Path
APP_PATH="/services/keepassxc"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/KeePassXC-2.7.10-x86_64.AppImage /usr/bin/keepassxc
ln -sv ${APP_PATH}/KeePassXC-2.7.10-x86_64.AppImage /usr/bin/KeePassXC

echo "Finished" | $LOGGER

EOF
