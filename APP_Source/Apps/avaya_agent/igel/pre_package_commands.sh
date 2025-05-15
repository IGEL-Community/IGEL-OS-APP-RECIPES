#!/bin/bash

mkdir -p "%root%/etc/avaya_agent"
cat <<"EOF" > "%root%/etc/avaya_agent/avaya_agent-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="avaya_agent_${1}"

# App Path
APP_PATH="/services/avaya_agent"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/opt/qt5.15.5 /opt/qt5.15.5

ln -sv ${APP_PATH}/usr/lib/avaya-agent /usr/lib/avaya-agent

ln -sv ${APP_PATH}/usr/share/avaya-agent /usr/share/avaya-agent

ln -sv ${APP_PATH}/usr/bin/AafdWatcher /usr/bin/AafdWatcher

ln -sv ${APP_PATH}/usr/bin/Agent-launcher /usr/bin/Agent-launcher

ln -sv ${APP_PATH}/usr/bin/AvayaAgent /usr/bin/AvayaAgent

ln -sv ${APP_PATH}/usr/bin/CrashReporter /usr/bin/CrashReporter

echo "Finished" | $LOGGER

EOF

