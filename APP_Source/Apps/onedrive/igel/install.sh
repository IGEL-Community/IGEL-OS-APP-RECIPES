#!/bin/bash
# For root services:
enable_system_service onedrive.service
# For user services:
#enable_system_user_service onedrive-user.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/onedrive.service
