#!/bin/bash

# Enable the tailscaled service
enable_system_service tailscaled.service

# Set proper permissions for systemd unit file
chmod 644 /lib/systemd/system/tailscaled.service
