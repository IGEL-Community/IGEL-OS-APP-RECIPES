#!/bin/bash
# For root services:
enable_system_service topaz.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/topaz.service
