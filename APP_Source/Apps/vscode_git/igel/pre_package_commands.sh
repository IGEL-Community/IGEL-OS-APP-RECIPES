#!/bin/bash

mkdir -p "%root%/etc/vscode_git"
cat <<"EOF" > "%root%/etc/vscode_git/vscode_git-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-vscode_git${1}"

# app path
APP_PATH="/services/vscode_git"

touch /userhome/Code/.gitconfig
ln -sv /userhome/Code/.gitconfig /userhome/.gitconfig | $LOGGER
ln -sv /services/vscode_git/usr/share/code/bin/code /services/vscode_git/usr/bin/code

#
# Turn off update check
#
if [ ! -e /userhome/.config/Code/User/settings.json ]; then
  mkdir -p /userhome/.config/Code/User
  chown -R user:users /userhome/.config/Code/User
  cat << "XEOF" > /userhome/.config/Code/User/settings.json
{
    "update.mode": "none"
}
XEOF
fi
chown -R user:users /userhome/.config/Code/User

echo "Finished" | $LOGGER

EOF
