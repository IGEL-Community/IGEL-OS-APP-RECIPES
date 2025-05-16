#!/bin/bash

mkdir -p "%root%/etc/bomgar"
cat <<"EOF" > "%root%/etc/bomgar/bomgar-init.sh"
#!/bin/bash
set -x
#trap read debug

ACTION="bomgar_${1}"

# App Path
APP_PATH="/services/bomgar"

#Detrermine bomgar installation file name
BOMGARDESKTOP=$(ls $APP_PATH/ | grep bomgar-scc)

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

# find bomgar persistent directory if already installed
BOMGARPERSIST=$(ls -a $APP_PATH/userhome/ | grep .bomgar-scc)

# find bomgar installation ID
BOMGARINSTID=$(ls -a /userhome/ | grep .bomgar-scc)

echo "Starting" | $LOGGER

if [ -f /userhome/.bomgar_installed/InstallTimeStamp.log ]; then
   . /userhome/.bomgar_installed/bomgar_install_dir.sh
   BOMGAR_CURR_VER=$(igelpkgctl list installed | grep bomgar | tr -d '\t')
   if [ "$BOMGAR_CURR_VER" != "$BOMGAR_VERSION" ]; then
      rm -f /userhome/.bomgar_installed/*
   fi
fi

if [ -f /userhome/.bomgar_installed/InstallTimeStamp.log ]; then
   #copy data into $BOMGAR_DIR
   su user -c "mkdir /userhome/$BOMGAR_DIR"
   su user -c "cp -R /userhome/.bomgar-scc/* /userhome/$BOMGAR_DIR"

   #launch bomgar
   su user -c "/userhome/$BOMGAR_DIR/start_pinned &"
   echo "Finished" | $LOGGER
   exit 0
else
   echo "Installed on "`date` >  /userhome/.bomgar_installed/InstallTimeStamp.log

   #Run bomgar installer as user
   chmod 777 $APP_PATH/$BOMGARDESKTOP
   su user -c "bash $APP_PATH/$BOMGARDESKTOP"

   #Wait for Bomgar install to finish and get directory name as BOMGARINSTID
   BOMGARINSTID=
   while [ -z "$BOMGARINSTID" ]; do
     BOMGARINSTID=$(ls -a /userhome/ | grep .bomgar-scc-)
     sleep 10
   done

   #Create directory and copy data to directory for persistence of install.
   echo "BOMGAR_DIR=$BOMGARINSTID" > /userhome/.bomgar_installed/bomgar_install_dir.sh | $LOGGER
   BOMGAR_VER=$(igelpkgctl list installed | grep bomgar | tr -d '\t')
   echo "BOMGAR_VERSION=$BOMGAR_VER" >> /userhome/.bomgar_installed/bomgar_install_dir.sh | $LOGGER
   cp -R /userhome/$BOMGARINSTID/* /userhome/.bomgar-scc | $LOGGER
   chown -R user:users /userhome/.bomgar-scc/* | $LOGGER

   su user -c "/userhome/$BOMGARINSTID/start_pinned &"
   echo "Finished" | $LOGGER
   exit 0
fi

EOF
