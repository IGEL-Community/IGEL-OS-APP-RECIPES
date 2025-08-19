#!/bin/bash

mkdir -p "%root%/etc/tailscale"
cat <<"EOF" > "%root%/etc/tailscale/tailscale-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="tailscale_${1}"

# App Path
APP_PATH="/services/tailscale"

LOGGER="logger -it ${ACTION}"

echo "Starting" | $LOGGER

#ln -svf /userhome/.config/tailscale-var-lib /var/lib/tailscale
nohup tailscale web > /root/tailscale-web.log 2>&1 &

echo "Finished" | $LOGGER

EOF
