#!/bin/bash

mkdir -p "%root%/etc/topaz"
cat <<"EOF" > "%root%/etc/topaz/topaz-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-topaz${1}"

# app path
APP_PATH="/services/topaz_sigplus_pro_c_object_library"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

# Linking files and folders on proper path
find ${APP_PATH} -printf "/%P\n" | while read DEST
do
  if [ ! -z "${DEST}" -a ! -e "${DEST}" ]; then
    # Remove the last slash, if it is a dir
    [ -d $DEST ] && DEST=${DEST%/} | $LOGGER
    if [ ! -z "${DEST}" ]; then
      ln -sv "${APP_PATH}/${DEST}" "${DEST}" | $LOGGER
    fi
  fi
done

echo "Finished" | $LOGGER

EOF
