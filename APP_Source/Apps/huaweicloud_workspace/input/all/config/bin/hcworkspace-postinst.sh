#!/bin/bash

function set_usb_permission() {
  local LOGIN_USER=$1
  if [ -n "${LOGIN_USER}" ] && [ "${LOGIN_USER}"x != "root"x ]; then
      echo "[info] set usb permission, required reboot computer"
      usermod -a -G dialout $LOGIN_USER
      echo "ATTRS{idProduct}==\"*\", ATTRS{idVendor}==\"*\", MODE=\"666\", OWNER=\"$LOGIN_USER\", GROUP=\"$LOGIN_USER\"" > /etc/udev/rules.d/40-allusb.rules
  fi
}

ACTION="hcworkspace_postinst"

# output to systemlog with ID amd tag
LOGGER="logger -it ${ACTION}"

echo "Starting - Configure Huawei Cloud Workspace Postinst" | $LOGGER


app_name=HuaweiCloudWorkspace
app_id=com.huawei.$app_name
INSTALL_PATH=/opt/apps/${app_id}/files/HDPViewer
CUSTOMIZED_PATH=/opt/apps/${app_id}/files/Workspace/.accessclient
ENTRIES_PATH=/opt/apps/${app_id}/entries
deviceName=$(cat /proc/cpuinfo | grep "Hardware" | awk '{print $3}')
deviceModel=$(cat /proc/cpuinfo | grep "Hardware" | awk '{print $4}')

baseVersion="20.0.0.0"
function versionLt() { test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; }

HCWORKSPACE_DIR="/services/hcworkspace"

mkdir -p /opt/apps
ln -svf ${HCWORKSPACE_DIR}/opt/apps/com.huawei.HuaweiCloudWorkspace /opt/apps/com.huawei.HuaweiCloudWorkspace | $LOGGER

# ��װ�����Ҫ��װ����ͨ��
echo "Install vchannels..."
export LD_LIBRARY_PATH=${INSTALL_PATH}/lib:$LD_LIBRARY_PATH
cd ${INSTALL_PATH}/3rd/virtualchannel
if [ ! -f hdpvcobjectsinitools ]; then
    echo "ERROR: hdpvcobjectsinitools cannot be found."
else
    ./hdpvcobjectsinitools > /dev/null 2>&1
fi

# �̳�R5C30 espace
if [ -f "${INSTALL_PATH}/3rd/virtualchannel/tchwdriver/tchwdriver.dll" ]; then
    ./hdpvcobjectsinitools -add tchwdriver tchwdriver.dll
fi

# ����б��ݵ������ļ�����лָ�����Ҫ��run��������deb������
#CONFIG_BACKUP_PATH="/opt/apps/${app_id}/files/conf_back"
#if [ -d ${CONFIG_BACKUP_PATH} ];then
    #echo "revert bakcup config for old run pack"
    #cp -rf ${CONFIG_BACKUP_PATH}/. ${INSTALL_PATH}/config
    #rm -rf ${CONFIG_BACKUP_PATH}
#fi

# ɾ��2.0CloudClient����ļ�
cloudClientName=fusionaccessclient
cloudClientId=com.huawei.${cloudClientName}
cloudClientInstallPath=/opt/apps/${cloudClientId}/files/HDPViewer

fileName="${cloudClientInstallPath}/LinuxClient/version.txt"
version=`grep "version" ${fileName} | awk 'BEGIN{FS=":"}{print $2}'`

#if [ -f "${fileName}" ]; then
    #if versionLt ${version} ${baseVersion}; then
        #echo "${version} is less than $baseVersion"
    #else
        ## ɾ�����������ļ�
        #autoStartPath="/etc/xdg/autostart/${cloudClientId}.desktop"
        #if [ -f ${autoStartPath} ]; then
            #echo "remove /etc/xdg/autostart/${cloudClientId}.desktop"
            #rm -f ${autoStartPath}
        #fi

        ## ɾ��Ӧ��ͼ��
        #appIcon="/usr/share/applications/${cloudClientId}.desktop"
        #if [ -f ${appIcon} ]; then
            #echo "delete ${appIcon}"
            #rm -f ${appIcon}
        #fi

        ## ɾ������ͼ��
        #cd /home
        #for user in *; do
            #desktopIcon="/home/${user}/Desktop"
            #if [ -d "$user"/Desktop ]; then
            #desktopIcon=/home/$user/Desktop
            #elif [ -f "$user"/.config/user-dirs.dirs ]; then
                ## ���û������ļ��л�ȡ��������
                #desktopName=`cat "$user"/.config/user-dirs.dirs | grep DESKTOP | tail -1 |cut -d '=' -f 2 | sed 's/$HOME\///g' | sed 's/\"//g'`
                #desktopIcon=/home/$user/$desktopName
            #fi

            #if [ -f "$desktopIcon"/${cloudClientId}.desktop ]; then
                #echo "remove $desktopIcon/${cloudClientId}.desktop"
                #rm -f "$desktopIcon"/${cloudClientId}.desktop
            #fi
        #done
    #fi
#fi

echo "begin remove ${cloudClientId}.desktop"

#cd /home
#for user in *; 
#do 
    #desktopIcon="/home/${user}/Desktop"
    #if [ -d "$user"/Desktop ]; then
        #desktopIcon=/home/$user/Desktop
    #elif [ -f "$user"/.config/user-dirs.dirs ]; then
        #desktopName=`cat "$user"/.config/user-dirs.dirs | grep DESKTOP | tail -1 |cut -d '=' -f 2 | sed 's/$HOME\///g' | sed 's/\"//g'`
        #desktopIcon=/home/$user/$desktopName
    #fi

    #if [ -f "$desktopIcon"/${cloudClientId}.desktop ]; then
        #echo "remove $desktopIcon/${cloudClientId}.desktop"
        #rm -f "$desktopIcon"/${cloudClientId}.desktop
    #fi
#done

# HT3300TC��ʹ���Դ�ffmpeg��stdc++
#HT3300_BASE_ENV=/usr/local/vdi/base.env
#if [ -f "$HT3300_BASE_ENV" ];then
    #source $HT3300_BASE_ENV
#fi

# HT3300TC��ʹ���Դ�ffmpeg��stdc++
#HT3300_BASE_ENV=/usr/local/vdi/sunniwellinfo.env
#if [ -f "$HT3300_BASE_ENV" ];then
    #source $HT3300_BASE_ENV
#fi

if [ ! -d "${INSTALL_PATH}/config/Workspace/" ]; then
    mkdir -p ${INSTALL_PATH}/config/Workspace

    # ���������ļ����ж�Workspace��config�ļ����Ƿ���ڣ����������ǵ�һ�ΰ�װ����Ҫ�̳�֮ǰ����
    configPath="/opt/apps/${cloudClientId}/files"
    if [ -d "${cloudClientInstallPath}/config" ]; then
        configPath="/opt/apps/${cloudClientId}/files/HDPViewer/config"
    else
        configPath="/opt/apps/${cloudClientId}/files/HDPClient/config"
    fi
    if [ "`ls -A ${INSTALL_PATH}/config/Workspace `" = "" ];then
        echo "revert config from ${configPath}"
        cp -rf ${configPath}/cloudclient/* ${INSTALL_PATH}/config/Workspace
        cp -rf ${configPath}/SetClientToTop.txt ${INSTALL_PATH}/config
        #������̹�900���޸�SetClientToTop.txt�ļ���������Ϊuser:user
        if [ "$SW_HARDWARE_MODEL" = "HT3300H" ] ; then
            chown user:user ${INSTALL_PATH}/config/SetClientToTop.txt
            chown -R user:user ${INSTALL_PATH}/config/Workspace
        fi

        # 1.8.10022.0�Ժ�FA�ͻ��˵�severs.xml�����ڣ�~/.config/Huawei/cloudclient/servers.xml
        #cd /home
        #for user in *; 
        #do 
            #if [ -f "/home/$user/.config/Huawei/cloudclient/servers.xml" ];then
                #echo "copy /home/$user/config/Huawei/cloudclient/servers.xml "
                #cp -rf /home/$user/.config/Huawei/cloudclient/servers.xml  ${INSTALL_PATH}/config/Workspace
            #fi
        #done
        if [ -f "/userhome/.config/Huawei/cloudclient/servers.xml" ];then
            echo "copy /userhome/user/config/Huawei/cloudclient/servers.xml "
            cp -rf /userhome/.config/Huawei/cloudclient/servers.xml  ${INSTALL_PATH}/config/Workspace
        fi
    fi
    lineNumber=`cat -n ${INSTALL_PATH}/config/Workspace/TClimits.xml | grep '<AccessLockShowLimited>' | awk '{print $1}'`
    sed -i "${lineNumber}c \        <AccessLockShowLimited>1</AccessLockShowLimited>" ${INSTALL_PATH}/config/Workspace/TClimits.xml
fi

echo "find libvdpau"
# ϵͳ��libvdpauλ�ò�ѯ
for i in {"/usr/lib64/libvdpau.so.1","/lib64/libvdpau.so.1","/usr/lib/mips64el-linux-gnuabi64/libvdpau.so.1","/usr/lib/mips64el-linux-gnu/libvdpau.so.1"}
  do
    echo "$i"
    if [ -a $i ];then
        echo "find system libvdpau in $i"
        rm ${INSTALL_PATH}/lib/libvdpau.so* -rf
        ln $i ${INSTALL_PATH}/lib/libvdpau.so -s
    fi
done

if [ "$SW_HARDWARE_MODEL" = "HT3300" ] || [ "$SW_HARDWARE_MODEL" = "HT3300H" ]; then
    echo "is ht3300 TC or ht3300H TC, rm ffmpeg"
    #ffmpeg
    rm ${INSTALL_PATH}/lib/libavcodec.so* -rf
    rm ${INSTALL_PATH}/lib/libavdevice.so* -rf
    rm ${INSTALL_PATH}/lib/libavfilter.so* -rf
    rm ${INSTALL_PATH}/lib/libavformat.so* -rf
    rm ${INSTALL_PATH}/lib/libavutil.so* -rf
    rm ${INSTALL_PATH}/lib/libswresample.so* -rf
    rm ${INSTALL_PATH}/lib/libswscale.so* -rf
fi

# HT5300TC�����û�������������vaapiӲ��ֻ��HT5300TC����Ч
HT5300_BASE_ENV=/usr/local/vdi/sunniwellinfo.env
if [ -f "$HT5300_BASE_ENV" ];then
    source $HT5300_BASE_ENV
fi

# �ָ����ݵ�keystore����Ҫ��run��������deb������
KEYSTORE_BACKUP_PATH="/opt/apps/${app_id}/files/keystore_back"
if [ -d ${KEYSTORE_BACKUP_PATH} ];then
    echo "revert keystore config for old run pack"
    mv ${KEYSTORE_BACKUP_PATH}/keystore ${INSTALL_PATH}/LinuxClient/
    rm -rf ${KEYSTORE_BACKUP_PATH}
fi

# �޸��ļ���Ȩ��cacerts
if [ -d ${INSTALL_PATH}/LinuxClient/keystore/cacerts ]; then
    # ��ȫ����: ֤����Թ�������, other������������
    chmod 644 -R ${INSTALL_PATH}/LinuxClient/keystore/cacerts/*
    chmod 755 ${INSTALL_PATH}/LinuxClient/keystore/cacerts
    if [ "$SW_HARDWARE_MODEL" = "HT3300H" ] ; then
        echo "is ht3300h TC, launch\cacerts"
        chmod 777 ${INSTALL_PATH}/LinuxClient/launch.sh
        chmod 777 ${INSTALL_PATH}/LinuxClient
        chmod 777 -R ${INSTALL_PATH}/LinuxClient/keystore/cacerts/*
        chmod 777 ${INSTALL_PATH}/LinuxClient/keystore/cacerts
        chown user: /sys/kernel/debug
    fi
fi

if [ "$SW_HARDWARE_MODEL" = "HT3300" ];then
    cd ${INSTALL_PATH}/lib
    if [ ! -d plugins ];then
        mkdir plugins
    fi
    cd plugins
    touch tc_ability_plugin_20.name
    chmod 777 tc_ability_plugin_20.name
    cp -f ${INSTALL_PATH}/lib_plugins/libPluginArmRK3568.so ${INSTALL_PATH}/lib/plugins/
    echo "${INSTALL_PATH}/lib/plugins/libPluginArmRK3568.so" >> tc_ability_plugin_20.name
fi

# ΪClientTool��sȨ��
chmod a+s ${INSTALL_PATH}/LinuxClient/ClientTool
echo "CREATECLOUDAPPCENTER: $CREATECLOUDAPPCENTER"

#Ϊ��ǰ�����û����������ݷ�ʽ
#cd /home
#for user in *; 
#do 
    #Desktop=/home/$user/Desktop
    #tccfgwizard_shortcut=tccfgwizard.desktop
    #if [ -d "$user"/Desktop ];then
        #Desktop=/home/$user/Desktop
    #elif [ -f "$user"/.config/user-dirs.dirs ];then
        ##���û������ļ��л�ȡ��������,[DTS2021070203VU9QP1400]
        #desktopName=`cat "$user"/.config/user-dirs.dirs | grep DESKTOP | tail -1 |cut -d '=' -f 2 | sed 's/$HOME\///g' | sed 's/\"//g'`
        #Desktop=/home/$user/$desktopName
    #fi
    #if [ -d $Desktop ];then
        #if [ "$SW_HARDWARE_MODEL" = "HT3300H" ] ; then
            #set_usb_permission ${user}
        #fi
        #cp -f ${ENTRIES_PATH}/applications/${app_id}.desktop $Desktop;
        #chmod +rx $Desktop/${app_id}.desktop
        #chown $user $Desktop/${app_id}.desktop
        ## ������򸲸ǣ���ֹ���ݸı�
        #if [ -f ${Desktop}/${tccfgwizard_shortcut} ]; then
            #cp -f ${CUSTOMIZED_PATH}/ui_resources/${tccfgwizard_shortcut} ${Desktop}/
        #fi
    #fi

    #���������
    #sharePath=/home/${user}/.local/share/applications
    #if [ ! -d $sharePath ];then
        #mkdir -p ${sharePath}
    #fi
    #chown $user:$user ${sharePath}
    #cp ${CUSTOMIZED_PATH}/ui_resources/hwcloud.desktop ${sharePath}
    #chmod +rx ${sharePath}/hwcloud.desktop
    #chown $user:$user ${sharePath}/hwcloud.desktop
    #cd ${sharePath}
    #su - $user -c 'xdg-mime default hwcloud.desktop x-scheme-handler/hwcloud'
    #cd /home
#done

echo "Set hwcloud.desktop to mime." 
xdg-mime default hwcloud.desktop 'x-scheme-handler/hwcloud'


cp -f ${CUSTOMIZED_PATH}/ui_resources/tccfgwizard.desktop ${INSTALL_PATH}/LinuxClient/
cp -f ${CUSTOMIZED_PATH}/ui_resources/startup.sh ${INSTALL_PATH}/LinuxClient/

configurationwizard_shortcut=ConfigurationWizard.desktop
if [ -f /usr/share/applications/${configurationwizard_shortcut} ]; then
    cp -f ${CUSTOMIZED_PATH}/ui_resources/${configurationwizard_shortcut} /usr/share/applications/
fi

#����UOS��${sharePath}��desktopЭ��
update-desktop-database

# uos���淶�����ļ�ϵͳ���Զ���������ļ��Ŀ�������uos���п���
#sys_os=`cat /etc/os-release | grep '^ID='`
#if [ $sys_os=="kylin" ]; then
    ## libpcre.so.3���ܴ��ڵ�·��������
    #if [ -e "/lib/mips64el-linux-gnu/libpcre.so.3" ]; then
        #rm -f ${INSTALL_PATH}/lib/libpcre.so.1
        #ln -s /lib/mips64el-linux-gnu/libpcre.so.3 ${INSTALL_PATH}/lib/libpcre.so.1
    #fi
    #if [ -e "/usr/lib/mips64el-linux-gnu/libpcre.so.3" ]; then
        #rm -f ${INSTALL_PATH}/lib/libpcre.so.1
        #ln -s /usr/lib/mips64el-linux-gnu/libpcre.so.3 ${INSTALL_PATH}/lib/libpcre.so.1
    #fi
    ## icon
    #cp -f ${ENTRIES_PATH}/icons/workspace_logo.png /usr/share/icons/hicolor/48x48
    #cp -f ${ENTRIES_PATH}/icons/HDPShareAppTray.png /usr/share/icons/hicolor/48x48
    ## �˵�����ݷ�ʽ
    #cp -f ${ENTRIES_PATH}/applications/${app_id}.desktop /usr/share/applications
    ## �Կ�������
    #cp -f ${ENTRIES_PATH}/applications/${app_id}.desktop /etc/xdg/autostart
#fi

if [ "$SW_HARDWARE_MODEL" = "HT3300H" ] ; then
    chmod 755 /etc/xdg/autostart
    export TERMINAL_CHIP_TYPE="m900"
fi

#if [[ ! -f "/usr/bin/kwin_wayland" ]] || [[ ! -f "/usr/bin/Xwayland" ]]; then
    ## ��ԷǺ�˼����waylandɾ������ͼ��desktop�ļ�
    #rm -f ${ENTRIES_PATH}/applications/com.huawei.Workspace.desktop
    #rm -f ${ENTRIES_PATH}/applications/com.huawei.qrdclient.desktop
    #rm -f ${ENTRIES_PATH}/applications/com.huawei.hdpviewer.desktop
    #rm -f ${ENTRIES_PATH}/applications/com.huawei.vncviewer.desktop
#fi

# �޸��û�Ȩ�����е�HDPShareAppTray��ʹ�õ����ļ����ļ���
if [ ! -f /opt/apps/${app_id}/files/WorkspaceLog ]; then
    mkdir /opt/apps/${app_id}/files/WorkspaceLog
fi
chmod 777 /opt/apps/${app_id}/files/WorkspaceLog

# HDPShareAppTray��Ҫ�������Ŀ¼������keystore
if [ ! -f ${INSTALL_PATH}/config/ ]; then
    mkdir -p ${INSTALL_PATH}/config/
fi
chmod 777 ${INSTALL_PATH}/config

# ����.upgrade_success�ļ���ʾ�������
#touch ${INSTALL_PATH}/.upgrade_success

cd ${CUSTOMIZED_PATH}
#./UninstallPreVer.sh $

echo "Finished - Configure Huawei Cloud Workspace Postinst" | $LOGGER