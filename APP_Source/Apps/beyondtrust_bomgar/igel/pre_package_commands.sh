#!/bin/bash

mkdir -p "%root%/etc/bomgar"
cat <<"EOF" > "%root%/etc/bomgar/bomgar-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="bomgar_${1}"

# App Path
APP_PATH="/services/bomgar"

#Detrermine bomgar installation file name

BOMGARDESKTOP=$(ls $APP_PATH/ | grep bomgar-scc)

# output to systemlog with ID amd tag

LOGGER="logger -it ${ACTION}"

su user -c "bash $APP_PATH/$BOMGARDESKTOP"

#Wait for Bomgar install to finish and get directory name as BOMGARINSTID

BOMGARINSTID=
while [ -z "$BOMGARINSTID" ]; do
   BOMGARINSTID=$(ls -a /userhome/ | grep .bomgar-scc-)
   sleep 5
done

su user -c "/userhome/$BOMGARINSTID/start_pinned &"

echo "Finished" | $LOGGER

EOF
