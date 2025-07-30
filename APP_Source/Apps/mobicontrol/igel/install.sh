#!/bin/bash
# For root services:
enable_system_service mobicontrol.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/mobicontrol.service
