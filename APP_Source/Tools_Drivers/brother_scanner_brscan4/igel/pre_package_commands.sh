#!/bin/bash

mkdir -p "%root%/etc/brother_scanner_brscan4"
cat <<"EOF" > "%root%/etc/brother_scanner_brscan4/brother_scanner_brscan4-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="brother_scanner_brscan4_${1}"

# App Path
APP_PATH="/services/brother_scanner_brscan4"

LOGGER="logger -it ${ACTION}"

echo "Staring" | $LOGGER

ln -svf ${APP_PATH}/opt/brother /opt/brother
${APP_PATH}/opt/brother/scanner/brscan4/setupSaneScan4 -i
${APP_PATH}/opt/brother/scanner/brscan4/udev_config.sh

echo "Finished" | $LOGGER

EOF
