#!/bin/bash

mkdir -p "%root%/etc/warp"
# Create corrected Warp desktop file
cat <<"EOF" > "%root%/etc/warp/dev.warp.Warp.desktop"
[Desktop Entry]
# The version of the desktop entry spec this conforms to.
Version=1.0

Type=Application

Name=Warp
GenericName=TerminalEmulator

Exec=/services/warp/Warp-x64.AppImage %U
StartupWMClass=dev.warp.Warp

Keywords=shell;prompt;command;commandline;cmd;

Icon=dev.warp.Warp

Categories=System;TerminalEmulator;

# Don't run this application within a terminal.
Terminal=false

# Register ourselves as the handler for warp:// URLs.
MimeType=x-scheme-handler/warp;
EOF

cat <<"EOF" > "%root%/etc/warp/warp-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="warp_${1}"

# App Path
APP_PATH="/services/warp"

LOGGER="logger -it ${ACTION}"

ln -sv ${APP_PATH}/Warp-x64.AppImage /usr/bin/warp

ln -sv /etc/warp/dev.warp.Warp.desktop /userhome/.local/share/applications/dev.warp.Warp.desktop

#xdg-mime default dev.warp.Warp.desktop x-scheme-handler/warp

echo "Finished" | $LOGGER

EOF
