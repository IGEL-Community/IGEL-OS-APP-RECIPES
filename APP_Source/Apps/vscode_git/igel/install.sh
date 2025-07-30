#!/bin/bash
# For root services:
enable_system_service vscode_git.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/vscode_git.service
