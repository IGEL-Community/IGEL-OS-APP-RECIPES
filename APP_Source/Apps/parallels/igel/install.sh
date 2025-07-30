#!/bin/bash
# For root services:
enable_system_service parallels_ras.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/parallels_ras.service
