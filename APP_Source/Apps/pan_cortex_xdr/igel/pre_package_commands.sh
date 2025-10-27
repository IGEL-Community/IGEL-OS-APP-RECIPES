#!/bin/bash

mkdir -p "%root%/etc/pan_cortex_xdr"
cat <<"EOF" > "%root%/etc/pan_cortex_xdr/pan_cortex_xdr-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="pan_cortex_xdr_${1}"

LOGGER="logger -it ${ACTION}"

echo "Start" | $LOGGER

# App Path
APP_PATH="/services/pan_cortex_xdr"
APP_RW_PATH="/services_rw/pan_cortex_xdr"

# link to /opt
ln -svf ${APP_PATH}/opt/paloaltonetworks /opt/paloaltonetworks | $LOGGER

# setup /etc/panw and collector.conf
#mkdir -p /etc/panw
cp ${APP_PATH}/collector.conf /etc/panw | $LOGGER
chmod 400 /etc/panw/collector.conf

# configure xml
/bin/bash /services/pan_cortex_xdr/config/bin/postinst.sh configure

echo "Finished" | $LOGGER

EOF