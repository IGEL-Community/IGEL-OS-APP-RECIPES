#!/bin/bash

mkdir -p "%root%/etc/sonicwall_netextender"
cat <<"EOF" > "%root%/etc/sonicwall_netextender/sonicwall_netextender-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="sonicwall_netextender_${1}"

# App Path
APP_PATH="/services/sonicwall_netextender"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

# from postinst

chmod 740 ${APP_PATH}/usr/local/netextender/NEService
mkdir -p /usr/local/netextender

# desktop file
if [ -f ${APP_PATH}/usr/local/netextender/com.sonicwall.NetExtender.desktop ]; then
	echo "Copy desktop file from ${APP_PATH}/usr/local/netextender/com.sonicwall.NetExtender.desktop to /usr/share/applications/com.sonicwall.NetExtender.desktop"
	cp ${APP_PATH}/usr/local/netextender/com.sonicwall.NetExtender.desktop /usr/share/applications/com.sonicwall.NetExtender.desktop
fi

if ! [ -x "$(command -v netExtender)" ]; then
	echo "Create symlink from ${APP_PATH}/usr/local/netextender/nxcli to /usr/sbin/netExtender"
	ln -s ${APP_PATH}/usr/local/netextender/nxcli /usr/sbin/netExtender
fi

if ! [ -x "$(command -v nxcli)" ]; then
	echo "Create symlink from ${APP_PATH}/usr/local/netextender/nxcli to /usr/sbin/nxcli"
	ln -s ${APP_PATH}/usr/local/netextender/nxcli /usr/sbin/nxcli
fi

if ! [ -x "$(command -v resolvconf)" ] && [ -x "$(command -v resolvectl)" ]; then
	resolvectl=$(command -v resolvectl)
	echo "Create symlink from ${resolvectl} to /usr/sbin/resolvconf"
	ln -s ${resolvectl} /usr/bin/resolvconf
fi

if ! [ -f ${APP_PATH}/usr/local/netextender/NetExtender ]; then
	ldconfig --version > /dev/null 2>&1
	if [ $? -eq 0 ]; then
		ldconfig -p | grep libwebkit2gtk-4.1 > /dev/null 2>&1
		if [ $? -eq 0 ]; then
			echo "Create symlink from ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_41 to /usr/local/netextender"
			ln -s ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_41 /usr/local/netextender/NetExtender
		else
			echo "Create symlink from ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_40 to /usr/local/netextender"
			ln -s ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_40 /usr/local/netextender/NetExtender
		fi
	else
		echo "Failed to detect libwebkit2gtk version, using libwebkit2gtk-4.0 as default"
		echo "Create symlink from ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_40 to /usr/local/netextender"
		ln -s ${APP_PATH}/usr/local/netextender/NetExtender_webkit2_40 /usr/local/netextender/NetExtender
	fi
fi

echo "Finished" | $LOGGER

EOF
