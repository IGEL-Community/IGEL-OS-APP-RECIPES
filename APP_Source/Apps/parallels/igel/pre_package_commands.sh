#!/bin/bash

mkdir -p "%root%/etc/parallels_ras"
cat <<"EOF" > "%root%/etc/parallels_ras/parallels_ras-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="parallels_ras_${1}"

# App Path
APP_PATH="/services/parallels_ras/opt/2X"
APP_OPT_LINK="/opt/2X"

LOGGER="logger -it ${ACTION}"

ln -svf ${APP_PATH} ${APP_OPT_LINK} | $LOGGER

# Run post install script to register icons, mimetypes, url schema and databases configurations
/opt/2X/Client/scripts/install.sh | $LOGGER

echo "Finished" | $LOGGER

EOF