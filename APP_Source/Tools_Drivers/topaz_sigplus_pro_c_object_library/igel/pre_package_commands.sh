#!/bin/bash

mkdir -p "%root%/etc/topaz"
cat <<"EOF" > "%root%/etc/topaz/topaz-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-topaz${1}"

# mount point path
MP=/services

# custom partition path
CP="${MP}/topaz_sigplus_pro_c_object_library"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

# Linking files and folders on proper path
find ${CP} -printf "/%P\n" | while read DEST
do
  if [ ! -z "${DEST}" -a ! -e "${DEST}" ]; then
    # Remove the last slash, if it is a dir
    [ -d $DEST ] && DEST=${DEST%/} | $LOGGER
    if [ ! -z "${DEST}" ]; then
      ln -sv "${CP}/${DEST}" "${DEST}" | $LOGGER
    fi
  fi
done

echo "Finished" | $LOGGER

exit 0

EOF
