#!/bin/bash

mkdir -p "%root%/etc/warp"
# Create corrected Warp desktop file
cat <<"EOF" > "%root%/etc/warp/dev.warp.Warp.desktop << 'EOF'
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

# Create user applications directory
echo "Creating user applications directory..." | $LOGGER
mkdir -p /userhome/.local/share/applications
ln -sv /etc/warp/dev.warp.Warp.desktop /userhome/.local/share/applications/dev.warp.Warp.desktop
echo "✓ User applications directory created/verified" | $LOGGER
echo

echo "✓ Warp desktop file created with correct executable path" | $LOGGER
echo

# Update user desktop database
echo "Updating user desktop database..." | $LOGGER
update-desktop-database ~/.local/share/applications/
echo "✓ User desktop database updated" | $LOGGER
echo

# Set Warp as handler for warp:// URLs
echo "Step 8: Setting Warp as handler for warp:// URLs..." | $LOGGER
xdg-mime default dev.warp.Warp.desktop x-scheme-handler/warp
echo "✓ Warp set as handler for warp:// URLs" | $LOGGER
echo

# Verify Warp URI handler configuration
echo "Verifying Warp URI handler configuration..." | $LOGGER
WARP_HANDLER=$(xdg-mime query default x-scheme-handler/warp)
echo "Warp URI handler: $WARP_HANDLER" | $LOGGER

if [ "$WARP_HANDLER" = "dev.warp.Warp.desktop" ]; then
    echo "✓ Warp URI handler is properly configured" | $LOGGER
else
    echo "⚠ Warp URI handler may not be set correctly" | $LOGGER
fi

echo "Finished" | $LOGGER

EOF
