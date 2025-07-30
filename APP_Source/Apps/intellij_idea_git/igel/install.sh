#!/bin/bash
# For root services:
enable_system_service intellij_idea_git.service

# Set proper permissions for systemd unit file
chmod 644 /etc/systemd/system/intellij_idea_git.service
