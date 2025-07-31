#!/bin/bash
# For root services:
enable_system_service apache2.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/apache2.service
