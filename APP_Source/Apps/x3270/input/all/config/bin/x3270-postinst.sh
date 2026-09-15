#!/bin/bash
#set -x
#trap read debug

ACTION="app-x3270-postinst"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Starting"

# app path
APP_PATH="/services/x3270"

touch /userhome/.config/x3270/.x3270connect
chown user:users /userhome/.config/x3270/.x3270connect
ln -svf /userhome/.config/x3270/.x3270connect /userhome/.x3270connect

FONTDIR="/services/x3270/usr/local/share/fonts/X11/misc"

mkfontscale "$FONTDIR"
mkfontdir "$FONTDIR"

echo "Finished"
