#!/bin/bash

mkdir -p "%root%/etc/rclone"
cat <<"EOF" > "%root%/etc/rclone/rclone-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="rclone_${1}"

# App Path
APP_PATH="/services/rclone"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/rclone-*-linux-amd64/rclone /usr/bin/rclone

echo "Finished" | $LOGGER

EOF

