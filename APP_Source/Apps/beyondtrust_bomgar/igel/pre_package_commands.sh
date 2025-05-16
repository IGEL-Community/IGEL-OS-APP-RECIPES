#!/bin/bash

mkdir -p "%root%/etc/bomgar"
cat <<"EOF" > "%root%/etc/bomgar/bomgar-init.sh"
#!/bin/bash
#set -x
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
   # killall bomgar processes
 	killall /userhome/$BOMGARPERSIST/bomgar-scc
	rm /userhome/$BOMGARPERSIST
   #symlink custom partition data directory to /userhome/
   . /userhome/.bomgar_installed/bomgar_install_dir.sh
   ln -s $APP_PATH/userhome/.bomgar-scc /userhome/$BOMGAR_DIR

   #launch bomgar
   su user -c "/userhome/$BOMGARINSTID/start_pinned &"
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
   echo "BOMGAR_DIR=$BOMGARINSTID" > /userhome/.bomgar_installed/bomgar_install_dir.sh
   cp -r /userhome/$BOMGARINSTID/* $APP_PATH/userhome/.bomgar-scc

   su user -c "/userhome/$BOMGARINSTID/start_pinned &"
   echo "Finished" | $LOGGER
   exit 0
fi

EOF
