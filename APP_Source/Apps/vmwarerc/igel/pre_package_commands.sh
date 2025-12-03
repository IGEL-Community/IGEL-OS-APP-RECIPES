#!/bin/bash

mkdir -p "%root%/etc/vmwarerc"
cat <<"EOF" > "%root%/etc/vmwarerc/vmwarerc-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="vmwarerc_${1}"

# App Path
APP_PATH="/services/vmwarerc"

LOGGER="logger -it ${ACTION}"

chmod a+x ${APP_PATH}/VMware-Remote-Console*.bundle
${APP_PATH}/VMware-Remote-Console*.bundle --eulas-agreed --required --console | $LOGGER

echo "Finished" | $LOGGER

EOF
