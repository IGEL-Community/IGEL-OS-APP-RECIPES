#!/bin/bash

mkdir -p "%root%/etc/intelij_idea_git"
cat <<"EOF" > "%root%/etc/intelij_idea_git/intelij_idea_git-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="app-intelij_idea_git${1}"

# app path
APP_PATH="/services/intelij_idea_git"

touch /userhome/IdeaProjects/.gitconfig
ln -sv /userhome/IdeaProjects/.gitconfig /userhome/.gitconfig | $LOGGER

ln -sv /services/intelij_idea_git/usr/local/idea* /usr/local/idea

echo "Finished" | $LOGGER

EOF
