#!/bin/bash

mkdir -p "%root%/etc/f5_vpn"
cat <<"EOF" > "%root%/etc/f5_vpn/f5_vpn-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="f5_vpn_${1}"

# App Path
APP_PATH="/services/f5_vpn"

LOGGER="logger -it ${ACTION}"

chown root ${APP_PATH}/opt/f5/vpn/svpn
chmod 4755 ${APP_PATH}/opt/f5/vpn/svpn
mkdir -p ${APP_PATH}/usr/local/lib/F5Networks/SSLVPN/var/run

cp -f ${APP_PATH}/opt/f5/vpn/com.f5.f5vpn.service /usr/share/dbus-1/services/
setcap cap_kill+ep ${APP_PATH}/opt/f5/vpn/f5vpn

chmod u+s ${APP_PATH}/usr/local/lib/F5Networks/SSLVPN/svpn_x86_64

cp -f ${APP_PATH}/opt/f5/epi/com.f5.f5epi.service /usr/share/dbus-1/services/

epi_config="${APP_PATH}/opt/f5/f5_epi.conf"
if ! [ -e "$epi_config" ]; then
touch "$epi_config"
chmod 644 "$epi_config"
sh -c "echo "ALLOW_UNTRUSTED_SERVERS=NO" >> '$epi_config'"
sh -c "echo "ALLOW_HTTP_SERVERS=NO" >> '$epi_config'"
fi

ln -sv ${APP_PATH}/opt/f5 /opt/f5

echo "Finished" | $LOGGER

EOF

