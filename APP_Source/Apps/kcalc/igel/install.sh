#!/bin/bash
# For root services:
enable_system_service kcalc.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/kcalc.service
