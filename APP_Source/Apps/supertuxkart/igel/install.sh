#!/bin/bash
enable_system_service supertuxkart-server.service
enable_user_service supertuxkart.service

# Set proper permissions for systemd unit files
chmod 644 /etc/systemd/system/supertuxkart-server.service
chmod 644 /etc/systemd/user/supertuxkart.service
