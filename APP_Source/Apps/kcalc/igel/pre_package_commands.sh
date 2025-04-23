#!/bin/bash

mkdir -p "%root%/etc/kcalc"
cat <<"EOF" > "%root%/etc/kcalc/kcalc-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-kcalc${1}"

# app path
APP_PATH="/services/kcalc"

touch /userhome/.config/kcalc/kcalcrc
chown user:users /userhome/.config/kcalc/kcalcrc
ln -sv /userhome/.config/kcalc/kcalcrc /userhome/.config/kcalcrc | $LOGGER

echo "Finished" | $LOGGER

EOF
