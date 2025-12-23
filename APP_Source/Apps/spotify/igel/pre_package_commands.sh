#!/bin/bash

mkdir -p "%root%/etc/spotify"
cat <<"EOF" > "%root%/etc/spotify/spotify-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="spotify_${1}"

# App Path
APP_PATH="/services/spotify"
APP_NAME=$(ls ${APP_PATH}/Spotify-*-x86_64.AppImage)

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

ln -svf ${APP_NAME} /usr/bin/spotify | $LOGGER

echo "Finished" | $LOGGER

EOF
