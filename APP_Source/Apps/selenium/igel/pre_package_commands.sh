#!/bin/bash

mkdir -p "%root%/etc/selenium"
cat <<"EOF" > "%root%/etc/selenium/selenium-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="selenium_${1}"

# App Path
APP_PATH="/services/selenium"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

echo "Finished" | $LOGGER

EOF
