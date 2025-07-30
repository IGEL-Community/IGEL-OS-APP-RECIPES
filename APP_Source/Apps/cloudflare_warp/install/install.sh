#!/bin/bash
# For root services:
enable_system_service warp-svc.service
# For user services:
enable_system_user_service warp-taskbar.service

# Set proper permissions for systemd unit files
chmod 644 /etc/systemd/system/warp-svc.service
chmod 644 /etc/systemd/user/warp-taskbar.service
