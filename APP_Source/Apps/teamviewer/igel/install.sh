#!/bin/bash
# For root services:
enable_system_service teamviewerd.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/teamviewerd.service
