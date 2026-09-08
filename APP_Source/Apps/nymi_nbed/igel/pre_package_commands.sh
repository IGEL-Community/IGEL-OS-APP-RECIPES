#!/bin/bash
#echo "[Unit]" > "%root%/lib/systemd/system/nbed.service"
#echo "Description=Nymi Bluetooth Endpoint Daemon (NBEd)" >> "%root%/lib/systemd/system/nbed.service"
#echo "After=network.target" >> "%root%/lib/systemd/system/nbed.service"
#echo "Requires=bluetooth.target" >> "%root%/lib/systemd/system/nbed.service"
#echo "" >> "%root%/lib/systemd/system/nbed.service"
#echo "[Service]" >> "%root%/lib/systemd/system/nbed.service"
#echo "Type=Exec" >> "%root%/lib/systemd/system/nbed.service"
#echo "ExecStart=/services/nbed/usr/bin/nbed -f" >> "%root%/lib/systemd/system/nbed.service"
#echo "ExecReload=-/usr/bin/pkill nbed" >> "%root%/lib/systemd/system/nbed.service"
#echo "ExecStop=-/usr/bin/pkill nbed" >> "%root%/lib/systemd/system/nbed.service"
#echo "Restart=always" >> "%root%/lib/systemd/system/nbed.service"
#echo "RestartSec=15" >> "%root%/lib/systemd/system/nbed.service"
#echo "" >> "%root%/lib/systemd/system/nbed.service"
#echo "[Install]" >> "%root%/lib/systemd/system/nbed.service"
#echo "WantedBy=multi-user.target" >> "%root%/lib/systemd/system/nbed.service"

cat << "EOF" > "%root%/lib/systemd/system/nbed.service"
[Unit]
Description=Nymi Bluetooth Endpoint Daemon (NBEd)
After=network.target
Requires=bluetooth.target

[Service]
Type=Exec
ExecStart=/services/nbed/usr/bin/nbed -f
ExecReload=-/usr/bin/pkill nbed
ExecStop=-/usr/bin/pkill nbed
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

