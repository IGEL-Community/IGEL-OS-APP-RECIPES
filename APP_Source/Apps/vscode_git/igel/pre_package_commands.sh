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

echo "Finished" | $LOGGER

EOF
