#!/bin/bash

mkdir -p "%root%/etc/twinkle"
cat <<"EOF" > "%root%/etc/twinkle/twinkle-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="twinkle_${1}"

# App Path
APP_PATH="/services/twinkle"
APP_PATH_RW="/services_rw/twinkle"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_PATH}/usr/share/twinkle /usr/share/twinkle

echo "Finished" | $LOGGER

EOF

