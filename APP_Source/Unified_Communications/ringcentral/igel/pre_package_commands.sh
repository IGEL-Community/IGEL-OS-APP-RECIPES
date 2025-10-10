#!/bin/bash

mkdir -p "%root%/etc/ringcentral"
cat <<"EOF" > "%root%/etc/ringcentral/ringcentral-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="ringcentral_${1}"

# App Path
APP_PATH="/services/ringcentral"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/RingCentral.Embeddable-*.AppImage /usr/bin/RingCentral
ln -sv ${APP_PATH}/RingCentral.Embeddable-*.AppImage /usr/bin/ringcentral

echo "Finished" | $LOGGER

EOF
