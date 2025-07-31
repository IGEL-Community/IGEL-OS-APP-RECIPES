#!/bin/bash
# For root services:
enable_system_service qz-tray.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/qz-tray.service
