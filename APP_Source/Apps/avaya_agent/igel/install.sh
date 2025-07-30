#!/bin/bash
# For root services:
enable_system_service avaya_agent.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/avaya_agent.service
