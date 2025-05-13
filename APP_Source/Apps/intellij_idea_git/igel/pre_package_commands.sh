#!/bin/bash

mkdir -p "%root%/etc/intellij_idea_git"
cat <<"EOF" > "%root%/etc/intellij_idea_git/intellij_idea_git-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-intellij_idea_git${1}"

# app path
APP_PATH="/services/intellij_idea_git"

touch /userhome/IdeaProjects/.gitconfig
ln -sv /userhome/IdeaProjects/.gitconfig /userhome/.gitconfig | $LOGGER

echo "Finished" | $LOGGER

EOF
